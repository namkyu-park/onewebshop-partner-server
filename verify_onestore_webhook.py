import json
from base64 import b64decode
from collections import OrderedDict
from Crypto.Hash import SHA512
from Crypto.PublicKey import RSA
from Crypto.Signature import PKCS1_v1_5
from sqlalchemy.orm import Session
from webshop_consume import get_env_data
import logging

logger = logging.getLogger(__name__)


def _load_rsa_public_key(key_material: str):
    """
    원스토어 라이선스 키는 PEM 또는 Base64(DER) 단일 문자열로 올 수 있다.
    """
    key_material = (key_material or "").strip()
    if not key_material:
        raise ValueError("empty license key")

    if key_material.startswith("-----"):
        rsa_key = RSA.import_key(key_material)
    else:
        rsa_key = RSA.import_key(b64decode(key_material))

    if rsa_key.has_private():
        return rsa_key.publickey()
    return rsa_key


def __verify(message, signature, pub_key):
    signer = PKCS1_v1_5.new(pub_key)
    digest = SHA512.new()
    if isinstance(message, str):
        message = message.encode("utf-8")
    digest.update(message)
    return signer.verify(digest, signature)

def verify_onestore_webhook(db: Session, rawMsg, client_id: str):
    env_data = get_env_data(db, client_id)
    if not env_data:
        raise Exception(f"원스토어 환경 데이터를 찾을 수 없습니다. client_id: {client_id}")
    
    if isinstance(rawMsg, bytes):
        rawMsg = rawMsg.decode("utf-8")
    jsonData = json.loads(rawMsg, object_pairs_hook=OrderedDict)
    signature = jsonData['signature']
    del jsonData['signature']
    originalMessage = json.dumps(jsonData, ensure_ascii=False, separators=(',', ':'))
    pub_key = _load_rsa_public_key(env_data.license_key)
    result = __verify(originalMessage, b64decode(signature), pub_key)

    logger.info(f"verify_onestore_webhook client_id: {client_id}, result: {result}")
    logger.info(f"verify_onestore_webhook rawMsg: {rawMsg}")
    logger.info(f"verify_onestore_webhook originalMessage: {originalMessage}")

    return result


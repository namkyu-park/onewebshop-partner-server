import requests
import logging
from models import OnestoreEnvData
from sqlalchemy.orm import Session
from webshop_onestore_env_api import get_onestore_env_data

logger = logging.getLogger(__name__)


def get_env_data(db: Session, client_id: str) -> OnestoreEnvData:
    """
    원스토어 환경 데이터 반환
    """
    env_data = get_onestore_env_data(db, client_id)
    if not env_data:
        raise Exception(f"원스토어 환경 데이터를 찾을 수 없습니다. client_id: {client_id}")
    return env_data

def get_pns_domain(env_data: OnestoreEnvData, environment: str = "SANDBOX") -> str:
    if environment == "SANDBOX":
        return env_data.pns_sandbox_domain
    else: # COMMERCIAL
        return env_data.pns_commercial_domain


def get_onestore_client_secret(env_data: OnestoreEnvData) -> str:
    if env_data and env_data.client_secret:
        return env_data.client_secret
    else:
        raise ValueError(f"원스토어 클라이언트 시크릿을 찾을 수 없습니다. client_id: {env_data}")

def get_onestore_access_token(client_id: str, domain: str) -> str:
    url = f"https://{domain}/v2/oauth/token"
    headers = {
        "Content-Type": "application/x-www-form-urlencoded",
        "Accept": "application/json",
    }

    body = {
        "client_id": client_id,
        "client_secret": get_onestore_client_secret(client_id),
        "grant_type": "client_credentials",
    }
    response = requests.post(url, data=body, headers=headers, timeout=10)

    if response.status_code == 200:
        response_json_data = response.json();
        print(response_json_data)
        logger.info(f"get_accesss_token: {response_json_data}")
        return response_json_data.get("access_token", "")
    else:
        raise Exception(f"원스토어 액세스 토큰 발급 실패: {response.text}")


def consume_onestore_purchase(db: Session, client_id: str, product_id: str, purchase_token: str, developerPayload: str, environment: str = "SANDBOX") -> dict:
    env_data = get_env_data(db, client_id)
    if not env_data:
        raise Exception(f"원스토어 환경 데이터를 찾을 수 없습니다. client_id: {client_id}")

    domain = get_pns_domain(env_data, environment)
    access_token = get_onestore_access_token(client_id, environment)
    if not access_token:
        raise Exception(f"원스토어 액세스 토큰 발급 실패")

    consume_url = f"https://{domain}/v7/apps/{client_id}/purchases/inapp/products/{product_id}/{purchase_token}/consume"
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json",
        "x-market-code": "MKT_ONE",
    }
    
    # Body는 빈 JSON 또는 필요한 데이터
    body = {
        "developerPayload": developerPayload,
    }
    
    try:
        logger.info(f"url: {consume_url}")
        logger.info(f"header: {headers}")
        logger.info(f"body: {body}")
        response = requests.post(consume_url, json=body, headers=headers, timeout=10)
        
        if response.status_code == 200:
            resp_data = response.json()
            result = resp_data.get("result", {})
            logger.info(f"consume response: {resp_data}")
            return resp_data
        else:
            logger.error(f"원스토어 consume 실패: status={response.status_code}, response={response.text}")
            return {}
            
    except requests.exceptions.Timeout:
        logger.error(f"원스토어 consume 타임아웃: {purchase_token}")
        return {}
    except Exception as e:
        logger.error(f"원스토어 consume 오류: {str(e)}")
        return {}
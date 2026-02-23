import requests
import logging

logger = logging.getLogger(__name__)

_ONESTORE_CLIENT_SECRET = {
    "WS00000026": "QVtVXBIMyRTt7Iz7PD08r4bKPBe5FgBzeMRgUe9jGKM=",
}

def get_domain(environment: str = "SANDBOX") -> str:
    """
    원스토어 도메인 반환
    """
    if environment == "SANDBOX":
        return "qa-sbpp.onestore.co.kr"
    else: # COMMERCIAL
        return "qa-pp.onestore.co.kr"

def get_onestore_client_secret(client_id: str) -> str:
    """
    원스토어 클라이언트 시크릿 반환
    """
    if client_id in _ONESTORE_CLIENT_SECRET:
        return _ONESTORE_CLIENT_SECRET[client_id]
    else:
        raise ValueError(f"원스토어 클라이언트 시크릿을 찾을 수 없습니다. client_id: {client_id}")

def get_onestore_access_token(client_id: str, environment: str = "SANDBOX") -> str:
    domain = get_domain(environment)
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


def consume_onestore_purchase(client_id: str, product_id: str, purchase_token: str, developerPayload: str, environment: str = "SANDBOX") -> dict:
    """
    원스토어 인앱 상품 구매 완료 처리 (Consume)
    
    Args:
        client_id: 앱의 클라이언트 ID
        purchase_token: 구매 토큰
        
    Returns:
        bool: 성공 여부
    """
    domain = get_domain(environment)
    url = f"https://{domain}/pc/v7/apps/{client_id}/purchases/inapp/{product_id}/{purchase_token}/consume"
    access_token = get_onestore_access_token(client_id, environment)
    if not access_token:
        raise Exception(f"원스토어 액세스 토큰 발급 실패")
    
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
        logger.info(f"url: {url}")
        logger.info(f"header: {headers}")
        logger.info(f"body: {body}")
        response = requests.post(url, json=body, headers=headers, timeout=10)
        
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
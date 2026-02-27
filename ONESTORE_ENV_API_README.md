# OnestoreEnvData CRUD API 테스트

원스토어 환경 데이터를 관리하는 API 테스트 가이드입니다.

## 📋 API 엔드포인트

| 메소드 | URL | 설명 |
|--------|-----|------|
| POST | `/onestore/env` | 환경 데이터 생성 |
| GET | `/onestore/env` | 모든 환경 데이터 조회 |
| GET | `/onestore/env/{client_id}` | 특정 환경 데이터 조회 |
| PUT | `/onestore/env/{client_id}` | 환경 데이터 수정 |
| DELETE | `/onestore/env/{client_id}` | 환경 데이터 삭제 |

## 🧪 테스트 시나리오

### 1. 환경 데이터 생성

```bash
curl -X POST "http://localhost:8080/onestore/env" \
  -H "Content-Type: application/json" \
  -d '{
    "client_id": "WS00000026",
    "license_key": "your_license_key",
    "client_secret": "QVtVXBIMyRTt7Iz7PD08r4bKPBe5FgBzeMRgUe9jGKM=",
    "pns_sandbox_domain": "https://qa-sbpp.onestore.co.kr",
    "pns_commercial_domain": "https://sbpp.onestore.co.kr"
  }'
```

**응답 예시:**
```json
{
  "result": {
    "code": "0000",
    "message": "생성 성공"
  },
  "envData": {
    "client_id": "WS00000026",
    "license_key": "your_license_key",
    "client_secret": "QVtVXBIMyRTt7Iz7PD08r4bKPBe5FgBzeMRgUe9jGKM=",
    "pns_sandbox_domain": "https://qa-sbpp.onestore.co.kr",
    "pns_commercial_domain": "https://sbpp.onestore.co.kr",
    "id": 1
  }
}
```

### 2. 모든 환경 데이터 조회

```bash
curl -X GET "http://localhost:8080/onestore/env"
```

**응답 예시:**
```json
{
  "result": {
    "code": "0000",
    "message": "조회 성공"
  },
  "envDataList": [
    {
      "client_id": "WS00000026",
      "license_key": "your_license_key",
      "client_secret": "QVtVXBIMyRTt7Iz7PD08r4bKPBe5FgBzeMRgUe9jGKM=",
      "pns_sandbox_domain": "https://qa-sbpp.onestore.co.kr",
      "pns_commercial_domain": "https://sbpp.onestore.co.kr",
      "id": 1
    }
  ]
}
```

### 3. 특정 환경 데이터 조회

```bash
curl -X GET "http://localhost:8080/onestore/env/WS00000026"
```

**응답 예시:**
```json
{
  "result": {
    "code": "0000",
    "message": "조회 성공"
  },
  "envData": {
    "client_id": "WS00000026",
    "license_key": "your_license_key",
    "client_secret": "QVtVXBIMyRTt7Iz7PD08r4bKPBe5FgBzeMRgUe9jGKM=",
    "pns_sandbox_domain": "https://qa-sbpp.onestore.co.kr",
    "pns_commercial_domain": "https://sbpp.onestore.co.kr",
    "id": 1
  }
}
```

### 4. 환경 데이터 수정

```bash
curl -X PUT "http://localhost:8080/onestore/env/WS00000026" \
  -H "Content-Type: application/json" \
  -d '{
    "license_key": "new_license_key",
    "pns_sandbox_domain": "https://new-qa-sbpp.onestore.co.kr"
  }'
```

**응답 예시:**
```json
{
  "result": {
    "code": "0000",
    "message": "수정 성공"
  },
  "envData": {
    "client_id": "WS00000026",
    "license_key": "new_license_key",
    "client_secret": "QVtVXBIMyRTt7Iz7PD08r4bKPBe5FgBzeMRgUe9jGKM=",
    "pns_sandbox_domain": "https://new-qa-sbpp.onestore.co.kr",
    "pns_commercial_domain": "https://sbpp.onestore.co.kr",
    "id": 1
  }
}
```

### 5. 환경 데이터 삭제

```bash
curl -X DELETE "http://localhost:8080/onestore/env/WS00000026"
```

**응답 예시:**
```json
{
  "result": {
    "code": "0000",
    "message": "삭제 성공"
  }
}
```

## 🔒 에러 응답

### 중복 client_id (400)

```json
{
  "detail": "이미 존재하는 client_id입니다: WS00000026"
}
```

### 데이터 없음 (404)

```json
{
  "detail": "해당 client_id를 찾을 수 없습니다: WS99999999"
}
```

### 잘못된 요청 (422)

```json
{
  "detail": [
    {
      "type": "missing",
      "loc": ["body", "client_id"],
      "msg": "Field required"
    }
  ]
}
```

## 🐍 Python 테스트 스크립트

```python
import requests

BASE_URL = "http://localhost:8080"

def test_create_env():
    """환경 데이터 생성 테스트"""
    response = requests.post(
        f"{BASE_URL}/onestore/env",
        json={
            "client_id": "WS00000026",
            "license_key": "test_license",
            "client_secret": "test_secret",
            "pns_sandbox_domain": "https://qa.onestore.co.kr",
            "pns_commercial_domain": "https://onestore.co.kr"
        }
    )
    print(f"생성: {response.status_code}")
    print(response.json())

def test_get_all_env():
    """모든 환경 데이터 조회 테스트"""
    response = requests.get(f"{BASE_URL}/onestore/env")
    print(f"전체 조회: {response.status_code}")
    print(response.json())

def test_get_env():
    """특정 환경 데이터 조회 테스트"""
    response = requests.get(f"{BASE_URL}/onestore/env/WS00000026")
    print(f"조회: {response.status_code}")
    print(response.json())

def test_update_env():
    """환경 데이터 수정 테스트"""
    response = requests.put(
        f"{BASE_URL}/onestore/env/WS00000026",
        json={
            "license_key": "updated_license"
        }
    )
    print(f"수정: {response.status_code}")
    print(response.json())

def test_delete_env():
    """환경 데이터 삭제 테스트"""
    response = requests.delete(f"{BASE_URL}/onestore/env/WS00000026")
    print(f"삭제: {response.status_code}")
    print(response.json())

if __name__ == "__main__":
    test_create_env()
    test_get_all_env()
    test_get_env()
    test_update_env()
    test_delete_env()
```

## 📊 데이터 구조

### OnestoreEnvData 모델

| 필드 | 타입 | 필수 | 설명 |
|------|------|------|------|
| `id` | Integer | Auto | 자동 생성 ID |
| `client_id` | String | ✅ | 원스토어 클라이언트 ID (고유키) |
| `license_key` | String | ✅ | 라이선스 키 |
| `client_secret` | String | ✅ | 클라이언트 시크릿 |
| `pns_sandbox_domain` | String | ✅ | Sandbox PNS 도메인 |
| `pns_commercial_domain` | String | ✅ | 상용 PNS 도메인 |

## 🎯 사용 예시

### webshop_consume.py에서 사용

```python
from sqlalchemy.orm import Session
import models

def get_onestore_client_secret(client_id: str, db: Session) -> str:
    """DB에서 클라이언트 시크릿 조회"""
    env_data = db.query(models.OnestoreEnvData).filter(
        models.OnestoreEnvData.client_id == client_id
    ).first()
    
    if not env_data:
        raise ValueError(f"client_id를 찾을 수 없습니다: {client_id}")
    
    return env_data.client_secret


def get_domain(client_id: str, environment: str, db: Session) -> str:
    """DB에서 도메인 조회"""
    env_data = db.query(models.OnestoreEnvData).filter(
        models.OnestoreEnvData.client_id == client_id
    ).first()
    
    if not env_data:
        raise ValueError(f"client_id를 찾을 수 없습니다: {client_id}")
    
    if environment == "SANDBOX":
        return env_data.pns_sandbox_domain
    else:
        return env_data.pns_commercial_domain
```

## 🚀 배포 후 설정

1. 서버 시작
2. Swagger UI 접속: `http://your-domain/docs`
3. "Onestore Environment" 섹션에서 API 테스트
4. 각 게임의 원스토어 환경 정보 등록

이제 하드코딩된 시크릿 대신 DB에서 관리할 수 있습니다! 🎉

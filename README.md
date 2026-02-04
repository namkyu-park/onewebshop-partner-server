# Test API - FastAPI + SQLite

Google Cloud Run에 배포 가능한 테스트용 REST API입니다.

## 기능

- FastAPI 기반 RESTful API
- SQLite 데이터베이스
- CRUD 작업 (생성, 조회, 수정, 삭제)
- 자동 API 문서 (Swagger UI)

## 로컬 실행

### 1. 가상환경 생성 및 활성화

```bash
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
```

### 2. 의존성 설치

```bash
pip install -r requirements.txt
```

### 3. 애플리케이션 실행

```bash
python main.py
# 또는
uvicorn main:app --reload --port 8080
```

### 4. API 테스트

브라우저에서 접속:
- API 문서: http://localhost:8080/docs
- 메인: http://localhost:8080/

## API 엔드포인트

### GET /
- 기본 정보 및 사용 가능한 엔드포인트 목록

### GET /health
- 헬스 체크

### POST /items/
- 아이템 생성
```json
{
  "name": "샘플 아이템",
  "description": "설명",
  "price": 10000,
  "is_active": true
}
```

### GET /items/
- 모든 아이템 조회
- 쿼리 파라미터: `skip`, `limit`

### GET /items/{item_id}
- 특정 아이템 조회

### PUT /items/{item_id}
- 아이템 수정

### DELETE /items/{item_id}
- 아이템 삭제

## Google Cloud Run 배포

### 1. Google Cloud CLI 설치 및 로그인

```bash
# gcloud CLI 설치 (미설치 시)
# https://cloud.google.com/sdk/docs/install

# 로그인
gcloud auth login

# 프로젝트 설정
gcloud config set project YOUR_PROJECT_ID
```

### 2. Docker 이미지 빌드 및 푸시

```bash
# 프로젝트 ID 설정
export PROJECT_ID=YOUR_PROJECT_ID
export SERVICE_NAME=webshop-partner-server
export REGION=asia-northeast3  # 서울 리전

# Artifact Registry에 저장소 생성 (최초 1회)
gcloud artifacts repositories create cloud-run-repo \
    --repository-format=docker \
    --location=$REGION \
    --description="Docker repository for Cloud Run"

# Docker 인증 설정
gcloud auth configure-docker ${REGION}-docker.pkg.dev

# 이미지 빌드
docker build -t ${REGION}-docker.pkg.dev/${PROJECT_ID}/cloud-run-repo/${SERVICE_NAME}:latest .

# 이미지 푸시
docker push ${REGION}-docker.pkg.dev/${PROJECT_ID}/cloud-run-repo/${SERVICE_NAME}:latest
```

### 3. Cloud Run에 배포

```bash
gcloud run deploy $SERVICE_NAME \
    --image ${REGION}-docker.pkg.dev/${PROJECT_ID}/cloud-run-repo/${SERVICE_NAME}:latest \
    --platform managed \
    --region $REGION \
    --allow-unauthenticated \
    --port 8080 \
    --memory 512Mi \
    --cpu 1 \
    --max-instances 10
```

### 4. 배포된 URL 확인

```bash
gcloud run services describe $SERVICE_NAME --region $REGION --format 'value(status.url)'
```

## 간편 배포 (Cloud Build 사용)

프로젝트 루트에서 실행:

```bash
gcloud run deploy test-api \
    --source . \
    --platform managed \
    --region asia-northeast3 \
    --allow-unauthenticated
```

Cloud Build가 자동으로 이미지를 빌드하고 배포합니다.

## 주의사항

### SQLite 데이터 영속성

Cloud Run은 stateless 환경이므로 컨테이너가 재시작되면 SQLite 데이터가 손실됩니다.

**프로덕션 환경에서는 다음 중 하나를 사용하세요:**
- Cloud SQL (PostgreSQL/MySQL)
- Firestore
- Cloud Storage + 파일 기반 DB

### 비용 절감

테스트용이므로 다음 설정을 권장합니다:
- `--memory 512Mi`: 최소 메모리
- `--cpu 1`: 최소 CPU
- `--max-instances 10`: 최대 인스턴스 제한

## 로컬 Docker 테스트

배포 전 로컬에서 Docker 이미지를 테스트할 수 있습니다:

```bash
# 이미지 빌드
docker build -t test-api .

# 컨테이너 실행
docker run -p 8080:8080 test-api

# 브라우저에서 http://localhost:8080 접속
```

## 환경 변수 설정 (선택사항)

Cloud Run 배포 시 환경 변수 추가:

```bash
gcloud run deploy test-api \
    --source . \
    --region asia-northeast3 \
    --set-env-vars "ENV=production,DEBUG=false"
```

## 모니터링

Cloud Run 콘솔에서 다음을 확인할 수 있습니다:
- 요청 수
- 응답 시간
- 에러율
- 로그

URL: https://console.cloud.google.com/run

## 문제 해결

### 로그 확인
```bash
gcloud run services logs read test-api --region asia-northeast3
```

### 서비스 삭제
```bash
gcloud run services delete test-api --region asia-northeast3
```

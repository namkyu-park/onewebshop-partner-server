# 배포 가이드

## 🏠 로컬 개발 환경

### 방법 1: Python 직접 실행

```bash
# 가상환경 생성 및 활성화
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# 의존성 설치
pip install -r requirements.txt

# 환경변수 설정 (선택)
export ENV=local

# 서버 실행
uvicorn main:app --reload --port 8080
```

데이터는 `./data/webshop-partner-server.db`에 저장됩니다.

### 방법 2: Docker Compose

```bash
# Docker Compose로 실행
docker-compose up --build

# 백그라운드 실행
docker-compose up -d --build

# 로그 확인
docker-compose logs -f

# 중지
docker-compose down
```

데이터는 `./data/webshop-partner-server.db`에 저장되며, 컨테이너를 삭제해도 유지됩니다.

---

## ☁️ Google Cloud Run 배포

### 사전 준비

1. **GCS 버킷 생성** (최초 1회만)

```bash
# 이미 생성됨
gcloud storage buckets create gs://onestore-webshop-data \
  --location=europe-west1 \
  --uniform-bucket-level-access
```

2. **프로젝트 ID 확인**

```bash
gcloud config get-value project
```

### 배포 명령어

```bash
# 변수 설정
PROJECT_ID=$(gcloud config get-value project)
SERVICE_NAME="onewebshop-partner-server"
REGION="europe-west1"
BUCKET_NAME="onestore-webshop-data"

# 이미지 빌드 및 푸시
gcloud builds submit --tag gcr.io/${PROJECT_ID}/${SERVICE_NAME}

# Cloud Run 배포 (Volume Mount 포함)
gcloud run deploy ${SERVICE_NAME} \
  --image gcr.io/${PROJECT_ID}/${SERVICE_NAME} \
  --platform managed \
  --region ${REGION} \
  --allow-unauthenticated \
  --execution-environment gen2 \
  --set-env-vars ENV=production \
  --add-volume name=sqlite-data,type=cloud-storage,bucket=${BUCKET_NAME} \
  --add-volume-mount volume=sqlite-data,mount-path=/data
```

### 한 줄 명령어 (전체)

```bash
PROJECT_ID=$(gcloud config get-value project) && \
gcloud builds submit --tag gcr.io/${PROJECT_ID}/onewebshop-partner-server && \
gcloud run deploy onewebshop-partner-server \
  --image gcr.io/${PROJECT_ID}/onewebshop-partner-server \
  --platform managed \
  --region europe-west1 \
  --allow-unauthenticated \
  --execution-environment gen2 \
  --set-env-vars ENV=production \
  --add-volume name=sqlite-data,type=cloud-storage,bucket=onestore-webshop-data \
  --add-volume-mount volume=sqlite-data,mount-path=/data
```

### 업데이트 배포 (코드 변경 후)

```bash
# 코드만 변경된 경우 (Volume 설정은 유지됨)
PROJECT_ID=$(gcloud config get-value project) && \
gcloud builds submit --tag gcr.io/${PROJECT_ID}/onewebshop-partner-server && \
gcloud run deploy onewebshop-partner-server \
  --image gcr.io/${PROJECT_ID}/onewebshop-partner-server \
  --region europe-west1
```

---

## 🔍 확인 및 모니터링

### 서비스 상태 확인

```bash
# 배포된 서비스 목록
gcloud run services list

# 서비스 상세 정보
gcloud run services describe onewebshop-partner-server --region europe-west1

# 서비스 URL 확인
gcloud run services describe onewebshop-partner-server \
  --region europe-west1 \
  --format='value(status.url)'
```

### 로그 확인

```bash
# 실시간 로그
gcloud run services logs tail onewebshop-partner-server --region europe-west1

# 최근 로그 50개
gcloud run services logs read onewebshop-partner-server \
  --region europe-west1 \
  --limit 50
```

### 데이터 백업 확인

```bash
# GCS 버킷에 저장된 DB 파일 확인
gcloud storage ls gs://onestore-webshop-data/

# DB 파일 다운로드 (백업)
gcloud storage cp gs://onestore-webshop-data/webshop-partner-server.db ./backup/
```

---

## 💰 비용 정보

### Cloud Storage (GCS)
- **요금**: $0.02/GB/월 (europe-west1)
- **예상**: DB 파일 10MB = 월 $0.0002 (거의 무료)

### Cloud Run
- **무료 할당량**: 월 200만 요청, 36만 GB-초
- **초과 시**: 요청당 $0.40/100만, vCPU-초당 $0.00002400

### 추정 월 비용
- 소규모 서비스: **$0~5** (무료 할당량 내)
- 중간 트래픽: **$5~20**

---

## ⚠️ 주의사항

1. **동시성 제한**: SQLite는 동시 쓰기에 약하므로, 트래픽이 많다면 Cloud SQL (PostgreSQL) 사용을 권장
2. **백업**: 중요한 데이터는 정기적으로 GCS 버킷 백업 설정
3. **환경 변수**: 
   - 로컬: `ENV=local` → `./data/` 사용
   - Cloud Run: `ENV=production` → `/data/` (Volume Mount) 사용

---

## 🔧 트러블슈팅

### 문제: 데이터가 저장되지 않음

```bash
# Volume Mount 설정 확인
gcloud run services describe onewebshop-partner-server \
  --region europe-west1 \
  --format='value(spec.template.spec.volumes)'

# 환경변수 확인
gcloud run services describe onewebshop-partner-server \
  --region europe-west1 \
  --format='value(spec.template.spec.containers[0].env)'
```

### 문제: 권한 오류

```bash
# Cloud Run 서비스 계정에 GCS 권한 추가
gcloud projects add-iam-policy-binding PROJECT_ID \
  --member="serviceAccount:SERVICE_ACCOUNT_EMAIL" \
  --role="roles/storage.objectAdmin"
```

### 문제: 빌드 실패

```bash
# 로컬에서 Docker 빌드 테스트
docker build -t test-app .
docker run -p 8080:8080 -e ENV=local test-app
```

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


### GET /health
- 헬스 체크

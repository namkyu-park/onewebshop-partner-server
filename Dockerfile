# Python 3.11 슬림 이미지 사용
FROM python:3.11-slim

# 작업 디렉토리 설정
WORKDIR /app

# 시스템 패키지 업데이트 및 필요한 패키지 설치
RUN apt-get update && apt-get install -y \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# 의존성 파일 복사 및 설치
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 애플리케이션 코드 복사
COPY . .

# SQLite 데이터베이스 디렉토리 권한 설정
RUN mkdir -p /app/data && chmod 777 /app/data

# Cloud Run에서 사용하는 포트 (기본 8080)
ENV PORT=8080

# 애플리케이션 실행
CMD uvicorn main:app --host 0.0.0.0 --port ${PORT}

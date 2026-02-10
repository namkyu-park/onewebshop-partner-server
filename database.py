from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import os

# SQLite 데이터베이스 파일 경로
# 환경: local (로컬 개발), production (Cloud Run)
ENV = os.getenv("ENV", "local")

if ENV == "production":
    # Cloud Run: Volume Mount 경로
    DB_PATH = "/data/webshop-partner-server.db"
else:
    # Local: 현재 디렉토리의 data 폴더
    DB_PATH = "./data/webshop-partner-server.db"
    # data 디렉토리가 없으면 생성
    os.makedirs("./data", exist_ok=True)

SQLALCHEMY_DATABASE_URL = f"sqlite:///{DB_PATH}"

# SQLite 연결 설정
engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False}  # SQLite에서 필요
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()


def init_db():
    """데이터베이스 초기화"""
    import models
    Base.metadata.create_all(bind=engine)


def get_db():
    """데이터베이스 세션 의존성"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

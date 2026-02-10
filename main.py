from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from database import init_db
from webshop_api import router as webshop_router

# 데이터베이스 테이블 생성
init_db()

app = FastAPI(
    title="Test API",
    description="Google Cloud Run에서 실행되는 테스트용 API",
    version="1.0.0"
)

# CORS 설정
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 라우터 등록
app.include_router(webshop_router, tags=["Webshop"])


@app.get("/")
def read_root():
    return {
        "message": "Test API is running!",
        "status": "healthy",
        "endpoints": {
            "docs": "/docs",
            "health": "/health",
            "gameserver": "/gameserver",
            "gameuser": "/gameuser",
        }
    }


@app.get("/health")
def health_check():
    return {"status": "ok"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8080)

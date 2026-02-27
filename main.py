from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from database import init_db
from webshop_api import router as webshop_router
from webshop_onestore_env_api import router as onestore_env_router
import logging
import sys

# 로깅 설정
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)

logger = logging.getLogger(__name__)



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
app.include_router(onestore_env_router, tags=["Onestore Environment"])


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

@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    # ❌ 실제 받은 요청 본문 출력 (여기서 문제 파악!)
    body = await request.body()
    print("== 422 ERROR ===")
    print(f"Request URL: {request.url}")
    print(f"Request Header: {request.headers}")
    print(f"Request Body: {body.decode()}")
    print(f"Validation Errors: {exc.errors()}")
    print("==================")
    
    # 기본 422 응답 반환
    return JSONResponse(
        status_code=422,
        content={"detail": exc.errors()}
    )

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8080)

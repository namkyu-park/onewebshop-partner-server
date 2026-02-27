from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
import models
import schemas
from database import get_db
import logging

logger = logging.getLogger(__name__)

# APIRouter 생성
router = APIRouter()


@router.post("/onestore/env", response_model=schemas.OnestoreEnvDataResponse)
def create_onestore_env(
    env_data: schemas.OnestoreEnvDataCreate,
    db: Session = Depends(get_db)
):
    """
    원스토어 환경 데이터 생성
    
    - client_id로 이미 존재하는 경우 에러 반환
    """
    # 중복 체크
    existing = get_onestore_env_data(db, env_data.client_id)
    
    if existing:
        raise HTTPException(
            status_code=400,
            detail=f"이미 존재하는 client_id입니다: {env_data.client_id}"
        )
    
    # 새 데이터 생성
    db_env_data = models.OnestoreEnvData(
        client_id=env_data.client_id,
        license_key=env_data.license_key,
        client_secret=env_data.client_secret,
        pns_sandbox_domain=env_data.pns_sandbox_domain,
        pns_commercial_domain=env_data.pns_commercial_domain
    )
    
    db.add(db_env_data)
    db.commit()
    db.refresh(db_env_data)
    
    logger.info(f"원스토어 환경 데이터 생성: client_id={env_data.client_id}")
    
    return schemas.OnestoreEnvDataResponse(
        result=schemas.ResponseResult(code="0000", message="생성 성공"),
        envData=db_env_data
    )


@router.get("/onestore/env", response_model=schemas.OnestoreEnvDataListResponse)
def get_onestore_env_list(db: Session = Depends(get_db)):
    """
    원스토어 환경 데이터 목록 조회
    """
    env_data_list = db.query(models.OnestoreEnvData).all()
    
    return schemas.OnestoreEnvDataListResponse(
        result=schemas.ResponseResult(code="0000", message="조회 성공"),
        envDataList=env_data_list
    )


@router.get("/onestore/env/{client_id}", response_model=schemas.OnestoreEnvDataResponse)
def get_onestore_env(
    client_id: str,
    db: Session = Depends(get_db)
):
    """
    특정 client_id의 원스토어 환경 데이터 조회
    """
    env_data = get_onestore_env_data(db, client_id)
    
    if not env_data:
        raise HTTPException(
            status_code=404,
            detail=f"해당 client_id를 찾을 수 없습니다: {client_id}"
        )
    
    return schemas.OnestoreEnvDataResponse(
        result=schemas.ResponseResult(code="0000", message="조회 성공"),
        envData=env_data
    )


@router.put("/onestore/env/{client_id}", response_model=schemas.OnestoreEnvDataResponse)
def update_onestore_env(
    client_id: str,
    env_data_update: schemas.OnestoreEnvDataUpdate,
    db: Session = Depends(get_db)
):
    """
    원스토어 환경 데이터 수정
    
    - 제공된 필드만 업데이트
    """
    env_data = get_onestore_env_data(db, client_id)
    
    if not env_data:
        raise HTTPException(
            status_code=404,
            detail=f"해당 client_id를 찾을 수 없습니다: {client_id}"
        )
    
    # 제공된 필드만 업데이트
    update_data = env_data_update.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        if field == "client_id": # skip client_id
            continue
        setattr(env_data, field, value)
    
    db.commit()
    db.refresh(env_data)
    
    logger.info(f"원스토어 환경 데이터 수정: client_id={client_id}")
    
    return schemas.OnestoreEnvDataResponse(
        result=schemas.ResponseResult(code="0000", message="수정 성공"),
        envData=env_data
    )


@router.delete("/onestore/env/{client_id}", response_model=schemas.ResposeBase)
def delete_onestore_env(
    client_id: str,
    db: Session = Depends(get_db)
):
    """
    원스토어 환경 데이터 삭제
    """
    env_data = get_onestore_env_data(db, client_id)
    
    if not env_data:
        raise HTTPException(
            status_code=404,
            detail=f"해당 client_id를 찾을 수 없습니다: {client_id}"
        )
    
    db.delete(env_data)
    db.commit()
    
    logger.info(f"원스토어 환경 데이터 삭제: client_id={client_id}")
    
    return schemas.ResposeBase(
        result=schemas.ResponseResult(code="0000", message="삭제 성공")
    )


def get_onestore_env_data(db: Session, client_id: str) -> Optional[models.OnestoreEnvData]:
    env_data = db.query(models.OnestoreEnvData).filter(
        models.OnestoreEnvData.client_id == client_id
    ).first()
    return env_data
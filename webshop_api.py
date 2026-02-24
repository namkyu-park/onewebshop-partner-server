from typing import List
from fastapi import APIRouter, Depends, Request, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
import models
import schemas
from database import get_db
import json
import logging
from webshop_consume import consume_onestore_purchase


# 로거 설정
logger = logging.getLogger(__name__)

# APIRouter 생성
router = APIRouter()

@router.post("/gameserver/{game_id}/list", response_model=schemas.GameServerListResponse)
def get_game_server_list(game_id: str, db: Session = Depends(get_db)):
    game_servers = db.query(models.GameServer).filter(models.GameServer.game_id == game_id).values(models.GameServer.server_id, models.GameServer.server_name)
    return schemas.GameServerListResponse(
        result=schemas.ResponseResult(
            code="0000", 
            message="Game servers retrieved successfully"),
        serverList=game_servers
    )


@router.post("/gameserver/create", response_model=schemas.ResposeBase)
def create_game_server(req: schemas.GameServerListRequest, db: Session = Depends(get_db)):
    for server in req.serverList:
        db_game_server = models.GameServer(game_id=req.game_id, server_id=server.server_id, server_name=server.server_name)
        db.add(db_game_server)
    db.commit()
    return schemas.ResposeBase(
        result=schemas.ResponseResult(
            code="0000", 
            message="Game servers created successfully"),
    )


@router.delete("/gameserver/{game_id}", response_model=schemas.ResposeBase)
def delete_all_game_server(game_id: str, db: Session = Depends(get_db)):
    db_game_servers = db.query(models.GameServer).filter(models.GameServer.game_id == game_id).all()
    if db_game_servers:
        for db_game_server in db_game_servers:
            db.delete(db_game_server)
        db.commit()
        return schemas.ResposeBase(
            result=schemas.ResponseResult(
                code="0000", 
                message="All game servers deleted successfully"),
        )
    else:
        return schemas.ResposeBase(
            result=schemas.ResponseResult(
                code="0001", 
                message="Game server not found"),
        )



@router.post("/gameuser/create", response_model=schemas.ResposeBase)
def create_game_user(req: schemas.GameUserCreateRequest, db: Session = Depends(get_db)):
    for user in req.userList:
        db_game_user = models.GameUser(game_id=req.game_id, user_id=user.user_id, server_id=user.server_id)
        db.add(db_game_user)
    db.commit()
    return schemas.ResposeBase(
        result=schemas.ResponseResult(
            code="0000", 
            message="Game users created successfully"),
    )


@router.delete("/gameuser/{game_id}/{user_id}", response_model=schemas.ResposeBase)
def delete_game_user(game_id: str, user_id: str, db: Session = Depends(get_db)):
    db_game_users = db.query(models.GameUser).filter(models.GameUser.game_id == game_id, models.GameUser.user_id == user_id).all()
    result = schemas.ResposeBase()
    if db_game_users:
        for db_game_user in db_game_users:
            db.delete(db_game_user)
        db.commit()
        return schemas.ResposeBase(
            result=schemas.ResponseResult(
                code="0000", 
                message="Game user deleted successfully"),
        )
    else:
        return schemas.ResposeBase(
            result=schemas.ResponseResult(
                code="0001", 
                message="Game user not found"),
        )


@router.get("/gameuser/{game_id}/list", response_model=schemas.GameUserListResponse)
def get_game_user_list(game_id: str, db: Session = Depends(get_db)):
    game_users = db.query(models.GameUser).filter(models.GameUser.game_id == game_id).all()
    return schemas.GameUserListResponse(
        result=schemas.ResponseResult(
            code="0000", 
            message="Game users retrieved successfully"),
        userList=game_users
    )


@router.post("/gameuser/check", response_model=schemas.GameUserCheckResponse)
def check_game_user(req: schemas.GameUserCheckRequest, db: Session = Depends(get_db)):
    # DB에서 조건에 맞는 사용자 조회
    db_game_user = db.query(models.GameUser).filter(
        models.GameUser.game_id == req.param.parentProdId,
        models.GameUser.user_id == req.param.serviceUserId,
        models.GameUser.server_id == req.param.serviceServerId
    ).first()
    
    if db_game_user:
        logger.info(f"{req.param.serviceUserId}는 게임서버({req.param.serviceServerId})에 등록된 사용자입니다. 대상상품ID: {req.param.parentProdId}, 인앱상품ID: {req.param.prodId}")
        return schemas.GameUserCheckResponse(
            result=schemas.ResponseResult(
                code="0000", 
                message="User found"),
            gameUser=db_game_user
        )
    else:
        logger.error(f"{req.param.serviceUserId}는 게임서버({req.param.serviceServerId})에 등록된 사용자가 아닙니다. 대상상품ID: {req.param.parentProdId}, 인앱상품ID: {req.param.prodId}")
        return schemas.GameUserCheckResponse(
            result=schemas.ResponseResult(
                code="0001", 
                message="User not found"),
            gameUser=None
        )

@router.post("/onestore_webshop/serverlist", response_model=schemas.GameServerListResponse)
def get_onestore_webshop_serverlist(req: schemas.OnestoreWebshopServerListRequest, db: Session = Depends(get_db)):
    game_servers = db.query(models.GameServer).filter(models.GameServer.game_id == req.param.prodId).all()
    logger.info(f"원스토어 웹샵({req.param.prodId}) 서버 목록 조회: {game_servers}")
    return schemas.GameServerListResponse(
        result=schemas.ResponseResult(
            code="0000", 
            message=f"Onestore Webshop({req.param.prodId}) servers retrieved successfully"),
        serverList=game_servers
    )

@router.post("/onestore_pns/notification", response_model=schemas.OnestorePNSResponse)
def receive_onestore_pns(
    pns_data: schemas.OnestorePNSRequest, 
    db: Session = Depends(get_db)
):
    """
    원스토어 PNS(Push Notification Service) 수신 엔드포인트
    
    원스토어에서 인앱상품 결제 또는 결제취소 발생 시 호출됩니다.
    
    - msgVersion: 3.1.0 (상용) 또는 3.1.0D (개발/Sandbox)
    - purchaseState: COMPLETED (결제완료) / CANCELED (취소)
    - environment: SANDBOX (개발) / COMMERCIAL (상용)
    - marketCode: MKT_ONE (원스토어) / MKT_GLB (원스토어 글로벌)
    """
    
    try:
        logger.info(f"원스토어 PNS 수신: purchaseId={pns_data.purchaseId}, state={pns_data.purchaseState}")
        
        # 중복 처리 방지: 이미 처리된 purchaseId인지 확인
        existing_pns = db.query(models.OnestorePNS).filter(
            models.OnestorePNS.purchase_id == pns_data.purchaseId
        ).first()
        
        if existing_pns:
            logger.warning(f"이미 처리된 purchaseId: {pns_data.purchaseId}")
            return schemas.OnestorePNSResponse(
                success=True,
                message="Already processed",
                purchaseId=pns_data.purchaseId
            )
        
        # paymentTypeList를 JSON 문자열로 변환
        payment_types_json = json.dumps([
            {"paymentMethod": pt.paymentMethod, "amount": pt.amount}
            for pt in pns_data.paymentTypeList
        ], ensure_ascii=False)
        
        # 원본 데이터를 JSON 문자열로 저장
        raw_data_json = pns_data.model_dump_json()
        
        # DB에 저장
        db_pns = models.OnestorePNS(
            msg_version=pns_data.msgVersion,
            client_id=pns_data.clientId,
            product_id=pns_data.productId,
            message_type=pns_data.messageType,
            purchase_id=pns_data.purchaseId,
            developer_payload=pns_data.developerPayload,
            purchase_time_millis=pns_data.purchaseTimeMillis,
            purchase_state=pns_data.purchaseState,
            price=pns_data.price,
            price_currency_code=pns_data.priceCurrencyCode,
            product_name=pns_data.productName,
            payment_types=payment_types_json,
            billing_key=pns_data.billingKey,
            is_test_mdn=pns_data.isTestMdn,
            purchase_token=pns_data.purchaseToken,
            environment=pns_data.environment,
            market_code=pns_data.marketCode,
            signature=pns_data.signature,
            raw_data=raw_data_json,
            serviceUserId=pns_data.serviceUserId,
            serviceServerId=pns_data.serviceServerId
        )
        
        db.add(db_pns)
        db.commit()
        db.refresh(db_pns)
        
        # 결제 상태에 따른 추가 처리
        if pns_data.purchaseState == "COMPLETED":
            # TODO: 여기에 게임 아이템 지급 로직 추가
            logger.info(f"결제 완료 처리: {pns_data.productName}( {pns_data.purchaseId} ), 가격: {pns_data.price}, 사용자: {pns_data.serviceUserId}, 서버: {pns_data.serviceServerId}")
            consume_onestore_purchase(pns_data.clientId, pns_data.productId, pns_data.purchaseToken, pns_data.developerPayload, "COMMERCIAL");
            
        elif pns_data.purchaseState == "CANCELED":
            logger.info(f"결제 취소 처리: {pns_data.productName}( {pns_data.purchaseId} ), 가격: {pns_data.price}, 사용자: {pns_data.serviceUserId}, 서버: {pns_data.serviceServerId}")
            # TODO: 여기에 게임 아이템 회수 로직 추가
        
        # 테스트폰 여부 로깅
        if pns_data.isTestMdn:
            logger.warning(f"테스트폰 결제: purchaseId={pns_data.purchaseId}")
        
        return schemas.OnestorePNSResponse(
            success=True,
            message="Notification received successfully",
            purchaseId=pns_data.purchaseId
        )
        
    except IntegrityError as e:
        db.rollback()
        logger.error(f"DB 무결성 오류: {str(e)}")
        # 중복 purchaseId로 인한 오류는 성공으로 처리 (멱등성 보장)
        if "purchase_id" in str(e).lower():
            return schemas.OnestorePNSResponse(
                success=True,
                message="Already processed (duplicate)",
                purchaseId=pns_data.purchaseId
            )
        raise HTTPException(status_code=500, detail="Database error")
        
    except Exception as e:
        db.rollback()
        logger.error(f"PNS 처리 중 오류 발생: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


@router.post("/onestore_pns/sandbox", response_model=schemas.OnestorePNSResponse)
def receive_onestore_pns(
    pns_data: schemas.OnestorePNSRequest, 
    db: Session = Depends(get_db)
):
    """
    원스토어 PNS(Push Notification Service) 수신 엔드포인트 (SANDBOX)
    
    원스토어에서 인앱상품 결제 또는 결제취소 발생 시 호출됩니다.
    
    - msgVersion: 3.1.0 (상용) 또는 3.1.0D (개발/Sandbox)
    - purchaseState: COMPLETED (결제완료) / CANCELED (취소)
    - environment: SANDBOX (개발) / COMMERCIAL (상용)
    - marketCode: MKT_ONE (원스토어) / MKT_GLB (원스토어 글로벌)
    """
    
    try:
        logger.info(f"원스토어 PNS 수신: purchaseId={pns_data.purchaseId}, state={pns_data.purchaseState}")
        
        # paymentTypeList를 JSON 문자열로 변환
        payment_types_json = json.dumps([
            {"paymentMethod": pt.paymentMethod, "amount": pt.amount}
            for pt in pns_data.paymentTypeList
        ], ensure_ascii=False)
        
        # 원본 데이터를 JSON 문자열로 저장
        # raw_data_json = pns_data.model_dump_json()
        
        # logger.info(f"원스토어 PNS 수신: purchaseId={pns_data.purchaseId}, state={pns_data.purchaseState}, raw_data={raw_data_json}")
        # 결제 상태에 따른 추가 처리
        if pns_data.purchaseState == "COMPLETED":
            logger.info(f"원스토어 PNS 결제 완료 처리: purchaseId={pns_data.purchaseId}, price={pns_data.price} {pns_data.priceCurrencyCode}")
            # TODO: 여기에 게임 아이템 지급 로직 추가
            consume_onestore_purchase(pns_data.clientId, pns_data.productId, pns_data.purchaseToken, pns_data.developerPayload, "SANDBOX");
            
        elif pns_data.purchaseState == "CANCELED":
            logger.info(f"원스토어 PNS 결제 취소 처리: purchaseId={pns_data.purchaseId}")
            # TODO: 여기에 게임 아이템 회수 로직 추가
        
        # 테스트폰 여부 로깅
        if pns_data.isTestMdn:
            logger.warning(f"원스토어 PNS 테스트폰 결제: purchaseId={pns_data.purchaseId}")
        
        return schemas.OnestorePNSResponse(
            success=True,
            message="Notification received successfully",
            purchaseId=pns_data.purchaseId
        )

    except Exception as e:
        db.rollback()
        logger.error(f"PNS 처리 중 오류 발생: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

@router.post("/onestore_webshop/consume", response_model=schemas.ResponseResult)
def force_consume(req: schemas.RequestForceConume):
    try: 
        result = consume_onestore_purchase(req.clientId, req.productId, req.purchaseToken, req.developerPayload, req.environment)
        return schemas.ResponseResult(
            code="",
            message=str(result)
        )

    except Exception as e:
        logger.error(f"Consume 처리 중 오류 발생: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


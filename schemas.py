from pydantic import BaseModel, ConfigDict, Field
from datetime import datetime
from typing import Optional
from typing import List

# GameServer 스키마
class GameServer(BaseModel):
    id: int
    game_id: str
    server_id: str
    server_name: str
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

class GameServerItem(BaseModel):
    model_config = ConfigDict(from_attributes=True, populate_by_name=True)

    server_id: str = Field(alias="serviceServerId")
    server_name: str = Field(alias="serviceServerName")

class GameServerListRequest(BaseModel):
    game_id: str
    serverList: List[GameServerItem] = []


class ResponseResult(BaseModel):
    code: str = "0000"
    message: str = ""


class ResposeBase(BaseModel):
    result: ResponseResult


class GameServerListResponse(ResposeBase):
    model_config = ConfigDict(from_attributes=True)
    serverList: List[GameServerItem] = []

# GameUser 스키마
class GameUser(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    user_id: str
    server_id: str

class GameUserCreateRequest(BaseModel):
    game_id: str
    userList: List[GameUser] = []

class GameUserListResponse(ResposeBase):
    model_config = ConfigDict(from_attributes=True)
    userList: List[GameUser] = []

# GameUser 조회 API용 스키마
class GameUserCheckParam(BaseModel):
    parentProdId: str
    prodId: str
    serviceUserId: str
    serviceServerId: str


class GameUserCheckRequest(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    param: GameUserCheckParam


class GameUserCheckResponse(ResposeBase):
    model_config = ConfigDict(from_attributes=True)
    gameUser: Optional[GameUser] = None


# 원스토어 PNS 스키마
class PaymentType(BaseModel):
    """결제 수단 정보"""
    paymentMethod: str
    amount: str

class OnestoreWebshopServerListParam(BaseModel):
    prodId: str

class OnestoreWebshopServerListRequest(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    param: OnestoreWebshopServerListParam

class OnestorePNSRequest(BaseModel):
    """원스토어 PNS Notification 요청 스키마"""
    msgVersion: str
    clientId: str
    productId: str
    messageType: str
    purchaseId: str
    developerPayload: Optional[str] = None
    purchaseTimeMillis: int
    purchaseState: str  # COMPLETED / CANCELED
    price: str
    priceCurrencyCode: str
    productName: Optional[str] = None
    paymentTypeList: List[PaymentType] = []
    billingKey: Optional[str] = None
    isTestMdn: bool
    purchaseToken: str
    environment: str  # SANDBOX / COMMERCIAL
    marketCode: str  # MKT_ONE / MKT_GLB
    signature: str


class OnestorePNSResponse(BaseModel):
    """원스토어 PNS Notification 응답 스키마"""
    success: bool
    message: str
    purchaseId: Optional[str] = None


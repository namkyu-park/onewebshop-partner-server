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
    prodId: str | None = Field(default=None) # Optional
    serviceUserId: str
    serviceServerId: str


class GameUserCheckRequest(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    param: GameUserCheckParam


class GameUserCheckResponse(ResposeBase):
    model_config = ConfigDict(from_attributes=True)
    gameUser: GameUser | None = Field(default=None)


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
    serviceUserId: str | None = Field(default=None)
    serviceServerId: str | None = Field(default=None)


class OnestorePNSResponse(BaseModel):
    """원스토어 PNS Notification 응답 스키마"""
    success: bool
    message: str
    purchaseId: Optional[str] = None

class RequestForceConume(BaseModel):
    clientId: str
    productId: str
    purchaseToken: str
    developerPayload: str
    environment: str


# OnestoreEnvData 스키마
class OnestoreEnvDataBase(BaseModel):
    """원스토어 환경 데이터 기본 스키마"""
    client_id: str
    license_key: str
    client_secret: str
    pns_sandbox_domain: str
    pns_commercial_domain: str


class OnestoreEnvDataCreate(OnestoreEnvDataBase):
    """원스토어 환경 데이터 생성 요청"""
    pass


class OnestoreEnvDataUpdate(BaseModel):
    """원스토어 환경 데이터 수정 요청"""
    license_key: Optional[str] = None
    client_secret: Optional[str] = None
    pns_sandbox_domain: Optional[str] = None
    pns_commercial_domain: Optional[str] = None


class OnestoreEnvData(OnestoreEnvDataBase):
    """원스토어 환경 데이터 응답"""
    model_config = ConfigDict(from_attributes=True)
    
    id: int


class OnestoreEnvDataListResponse(BaseModel):
    """원스토어 환경 데이터 목록 응답"""
    result: ResponseResult = ResponseResult()
    envDataList: List[OnestoreEnvData] = []


class OnestoreEnvDataResponse(BaseModel):
    """원스토어 환경 데이터 단일 응답"""
    result: ResponseResult = ResponseResult()
    envData: Optional[OnestoreEnvData] = None
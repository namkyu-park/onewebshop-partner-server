from sqlalchemy import Column, Integer, String, Float, Boolean, DateTime, Text, BigInteger
from sqlalchemy.sql import func
from database import Base

class GameServer(Base):
    __tablename__ = "game_servers"
    id = Column(Integer, primary_key=True, index=True)
    game_id = Column(String, index=True)
    server_id = Column(String, index=True)
    server_name = Column(String, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

class GameUser(Base):
    __tablename__ = "game_users"
    id = Column(Integer, primary_key=True, index=True)
    game_id = Column(String, index=True)
    user_id = Column(String, index=True)
    server_id = Column(String, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())


class OnestorePNS(Base):
    """원스토어 PNS Notification 저장 테이블"""
    __tablename__ = "onestore_pns_notifications"
    
    id = Column(Integer, primary_key=True, index=True)
    msg_version = Column(String(20), nullable=False)
    client_id = Column(String(50), index=True, nullable=False)
    product_id = Column(String(50), index=True, nullable=False)
    message_type = Column(String(50), nullable=False)
    purchase_id = Column(String(100), unique=True, index=True, nullable=False)
    developer_payload = Column(String(255), nullable=True)
    purchase_time_millis = Column(BigInteger, nullable=False)
    purchase_state = Column(String(20), index=True, nullable=False)  # COMPLETED / CANCELED
    price = Column(String(20), nullable=False)
    price_currency_code = Column(String(10), nullable=False)
    product_name = Column(String(255), nullable=True)
    payment_types = Column(Text, nullable=True)  # JSON string
    billing_key = Column(String(255), nullable=True)
    is_test_mdn = Column(Boolean, default=False)
    purchase_token = Column(Text, nullable=False)
    environment = Column(String(20), nullable=False)  # SANDBOX / COMMERCIAL
    market_code = Column(String(20), nullable=False)  # MKT_ONE / MKT_GLB
    signature = Column(Text, nullable=False)
    raw_data = Column(Text, nullable=True)  # 원본 JSON 데이터 저장
    serviceUserId = Column(String(255), nullable=True)
    serviceServerId = Column(String(255), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
from sqlalchemy import Column, Integer, DateTime, String, Numeric, Enum, UUID
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.dialects.postgresql import JSONB
from mkk.domain.models import Currency, Status


Base = declarative_base()

# TODO not null
class Payment(Base):
    __tablename__ = "payments"

    id = Column(Integer, primary_key=True, index=True)
    amount = Column(Numeric, nullable=False)
    currency = Column("currency", Enum(Currency), nullable=False)
    description = Column(String, nullable=False)
    status = Column("status", Enum(Status), nullable=False)
    idempotency_key = Column(UUID, nullable=False)
    url = Column(String, nullable=False)
    meta = Column(JSONB, nullable=False)
    created_at = Column(DateTime, nullable=False)
    processed_at = Column(DateTime)

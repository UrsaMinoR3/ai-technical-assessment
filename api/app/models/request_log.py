from datetime import datetime, timezone

from sqlalchemy import Column, DateTime, Float, Integer, String, Text

from ..core.database import Base


class RequestLog(Base):
    __tablename__ = "request_logs"

    id = Column(Integer, primary_key=True, index=True)
    timestamp = Column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)
    endpoint = Column(String(100), nullable=False)
    input_data = Column(Text)
    output_ref = Column(Text)
    external_usage = Column(String(500))
    latency_ms = Column(Float)
    http_status = Column(Integer)

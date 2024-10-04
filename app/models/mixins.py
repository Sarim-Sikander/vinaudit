from sqlalchemy import Column, TIMESTAMP
from sqlalchemy.sql import func


class TimeAuditMixin:
    created_at = Column(
        TIMESTAMP(timezone=True), nullable=False, server_default=func.now()
    )

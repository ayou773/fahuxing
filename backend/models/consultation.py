import uuid
from sqlalchemy import Column, String, Text, DateTime, func
from sqlalchemy.dialects.postgresql import UUID
from models.database import Base


class Consultation(Base):
    """法律咨询记录模型"""

    __tablename__ = "consultations"

    # 主键 - UUID
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    user_id = Column(String(64), nullable=False, default="anonymous", index=True, doc="用户ID")
    query = Column(Text, nullable=False, index=True, doc="用户提问")
    context = Column(Text, nullable=True, doc="上下文信息")
    response = Column(Text, nullable=False, doc="AI回答")
    case_type = Column(String(32), nullable=False, default="civil", doc="案件类型")

    # 创建时间
    created_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
        doc="创建时间"
    )

    def __repr__(self):
        return f"<Consultation(id={self.id}, query={self.query[:30]}...)>"

    def to_dict(self):
        """转换为字典"""
        return {
            "id": str(self.id),
            "user_id": self.user_id,
            "query": self.query,
            "context": self.context,
            "response": self.response,
            "case_type": self.case_type,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }
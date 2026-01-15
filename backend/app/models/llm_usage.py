"""LLM usage tracking model."""
from datetime import datetime
from sqlalchemy import Column, Integer, String, Float, Boolean, DateTime, ForeignKey
from sqlalchemy.orm import relationship

from app.database import Base


class LLMUsage(Base):
    """Track LLM API usage and costs."""

    __tablename__ = "llm_usage"

    id = Column(Integer, primary_key=True, index=True)
    interview_id = Column(Integer, ForeignKey("interviews.id"), nullable=False, index=True)
    agent_name = Column(String, nullable=False, index=True)
    model = Column(String, nullable=False)
    prompt_tokens = Column(Integer, nullable=False)
    completion_tokens = Column(Integer, nullable=False)
    total_tokens = Column(Integer, nullable=False)
    estimated_cost = Column(Float, nullable=False)
    cached = Column(Boolean, default=False, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    # Relationship
    interview = relationship("Interview", back_populates="llm_usage")

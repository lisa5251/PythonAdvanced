
from sqlalchemy import Column, Integer, Text, ForeignKey, DateTime, Float
from sqlalchemy.sql import func

from app.database import Base


class Analysis(Base):
    __tablename__ = "analyses"

    id = Column(Integer, primary_key=True, index=True)

    resume_id = Column(
        Integer,
        ForeignKey("resumes.id"),
        nullable=False
    )

    job_description = Column(Text, nullable=False)

    match_score = Column(Float, nullable=False)

    matched_skills = Column(Text, nullable=True)

    missing_skills = Column(Text, nullable=True)

    feedback = Column(Text, nullable=True)

    created_at = Column(
        DateTime(timezone=True),
        server_default=func.now()
    )

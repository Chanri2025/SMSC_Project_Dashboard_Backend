from database import db
from sqlalchemy import Column, Integer, String, Float, JSON, Boolean, BigInteger
from datetime import datetime


class Project(db.Model):
    __tablename__ = "project"

    id = Column(BigInteger, primary_key=True)
    project_name = Column(String(255), nullable=False)
    project_subparts = Column(JSON, nullable=False, default=[])
    total_estimate_hrs = Column(Float, default=0)
    total_elapsed_hrs = Column(Float, default=0)
    assigned_ids = Column(JSON, nullable=False, default=[])
    is_completed = Column(Boolean, nullable=False, default=False)
    created_by = Column(BigInteger, nullable=False)
    client_id = Column(BigInteger, nullable=False, default=1)
    created_at = Column(db.DateTime, default=datetime.utcnow)
    updated_at = Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

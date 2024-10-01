from .database import DatabaseInterface, get_database_interface
import sqlalchemy as sa
from sqlalchemy.orm import relationship
from sqlalchemy import Enum
from datetime import datetime as dt
from typing import List, Dict, Optional
from pydantic import BaseModel
from enum import Enum as PyEnum
from sqlalchemy import Column, Integer, String, Boolean, JSON, ForeignKey


Base = get_database_interface().get_declarative_base()

# Model for BoletimUrna
class BoletimUrnaModel(Base):
    __tablename__ = 'boletim_urna'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    evaluator_phone = Column(String(15), nullable=False) 
    type = Column(String, nullable=False)
    finished = Column(Boolean, nullable=False)
    last_carg = Column(Integer, nullable=False)
    last_party = Column(Integer, nullable=True)
    open_steps = Column(JSON, nullable=True)  # Stores list of open steps
    header = Column(JSON, nullable=False)  # JSON representation of the header
    content = Column(JSON, nullable=False)  # JSON representation of the content
    created_at = Column(sa.DateTime, default=dt.now)
    updated_at = Column(sa.DateTime, default=dt.now, onupdate=dt.now)

class EvaluatorModel(Base):
    __tablename__ = 'evaluator'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    phone_number = Column(String(15), nullable=False)
    section = Column(String(5), nullable=False)
    zone = Column(String(5), nullable=False)
    city = Column(String(50), nullable=False)
    created_at = Column(sa.DateTime, default=dt.now)
    updated_at = Column(sa.DateTime, default=dt.now, onupdate=dt.now)
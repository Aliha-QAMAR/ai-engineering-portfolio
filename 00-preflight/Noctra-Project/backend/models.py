from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime, timezone
from backend.database import Base

def utcnow():
    return datetime.now(timezone.utc)

class User(Base):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True)
    codename = Column(String(50), unique=True, nullable=False)
    password_hash = Column(String(200), nullable=False)
    clearance_level = Column(String(20), default='alpha')
    created_at = Column(DateTime, default=utcnow)
    
    investigations = relationship('Investigation', back_populates='user')
    memories = relationship('Memory', back_populates='user')

class Investigation(Base):
    __tablename__ = 'investigations'
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'))
    case_number = Column(String(50), unique=True, nullable=False)
    case_name = Column(String(100), nullable=False)
    description = Column(Text)
    status = Column(String(20), default='active')
    created_at = Column(DateTime, default=utcnow)
    updated_at = Column(DateTime, default=utcnow, onupdate=utcnow)
    
    user = relationship('User', back_populates='investigations')
    evidence = relationship('Evidence', back_populates='investigation')
    logs = relationship('InvestigationLog', back_populates='investigation')
    memories = relationship('Memory', back_populates='investigation')

class Evidence(Base):
    __tablename__ = 'evidence'
    id = Column(Integer, primary_key=True)
    investigation_id = Column(Integer, ForeignKey('investigations.id'))
    filename = Column(String(255))
    file_type = Column(String(20))
    file_path = Column(String(255))
    analysis_result = Column(Text)
    uploaded_at = Column(DateTime, default=utcnow)
    
    investigation = relationship('Investigation', back_populates='evidence')

class InvestigationLog(Base):
    __tablename__ = 'investigation_logs'
    id = Column(Integer, primary_key=True)
    investigation_id = Column(Integer, ForeignKey('investigations.id'))
    step_type = Column(String(50))
    content = Column(Text)
    tool = Column(String(60))          # which safe tool produced this step (if any)
    data = Column(Text)                # JSON: structured findings for the report
    timestamp = Column(DateTime, default=utcnow)
    
    investigation = relationship('Investigation', back_populates='logs')

class Memory(Base):
    __tablename__ = 'memories'
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'))
    key = Column(String(100))
    value = Column(Text)
    investigation_id = Column(Integer, ForeignKey('investigations.id'), nullable=True)
    created_at = Column(DateTime, default=utcnow)
    
    user = relationship('User', back_populates='memories')
    investigation = relationship('Investigation', back_populates='memories')

class Note(Base):
    __tablename__ = 'notes'
    id = Column(Integer, primary_key=True)
    investigation_id = Column(Integer, ForeignKey('investigations.id'))
    body = Column(Text)
    pinned = Column(Integer, default=0)     # 1 = extracted onto the board as a sticky note
    pin_x = Column(Integer, nullable=True)  # sticky note position on the board canvas
    pin_y = Column(Integer, nullable=True)
    created_at = Column(DateTime, default=utcnow)
    updated_at = Column(DateTime, default=utcnow, onupdate=utcnow)

class Clue(Base):
    """A candidate or confirmed investigative clue extracted from evidence.
    status: candidate → (confirmed | rejected). Placement on the board is
    tracked by placed/board_x/board_y."""
    __tablename__ = 'clues'
    id = Column(Integer, primary_key=True)
    investigation_id = Column(Integer, ForeignKey('investigations.id'))
    evidence_id = Column(Integer, ForeignKey('evidence.id'), nullable=True)
    title = Column(String(120))
    description = Column(Text)
    signal = Column(String(120))          # e.g. "Unusually large transaction"
    entity = Column(String(120))          # e.g. "Meridian Holdings"
    source = Column(String(255))          # source evidence filename
    source_location = Column(String(120)) # row/date/page if known
    clue_type = Column(String(40), default='fact')  # fact | pattern | inference
    confidence = Column(Integer, default=50)
    status = Column(String(20), default='candidate')
    placed = Column(Integer, default=0)   # 0/1 on the board
    board_x = Column(Integer, default=0)
    board_y = Column(Integer, default=0)
    origin = Column(String(40), default='evidence')  # evidence | previous_case
    created_at = Column(DateTime, default=utcnow)

class Relationship(Base):
    """A connection the investigator draws between two clues on the board.
    status: supported | rejected (evaluated against evidence basis)."""
    __tablename__ = 'relationships'
    id = Column(Integer, primary_key=True)
    investigation_id = Column(Integer, ForeignKey('investigations.id'))
    source_clue_id = Column(Integer, ForeignKey('clues.id'))
    target_clue_id = Column(Integer, ForeignKey('clues.id'))
    relationship_type = Column(String(60))
    status = Column(String(20), default='supported')
    evidence_basis = Column(Text)
    confidence = Column(Integer, default=50)
    created_at = Column(DateTime, default=utcnow)

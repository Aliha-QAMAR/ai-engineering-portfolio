import os
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker, declarative_base
from contextlib import contextmanager

from backend.config import Config

engine = create_engine(Config.DATABASE_URL)
db_session = scoped_session(sessionmaker(autocommit=False,
                                         autoflush=False,
                                         bind=engine))

Base = declarative_base()
Base.query = db_session.query_property()

def _ensure_columns():
    """Add columns introduced after a DB may already exist (SQLite-safe)."""
    from sqlalchemy import inspect, text
    try:
        insp = inspect(engine)
        if 'investigation_logs' in insp.get_table_names():
            cols = {c['name'] for c in insp.get_columns('investigation_logs')}
            with engine.begin() as conn:
                if 'tool' not in cols:
                    conn.execute(text('ALTER TABLE investigation_logs ADD COLUMN tool VARCHAR(60)'))
                if 'data' not in cols:
                    conn.execute(text('ALTER TABLE investigation_logs ADD COLUMN data TEXT'))
        if 'notes' in insp.get_table_names():
            cols = {c['name'] for c in insp.get_columns('notes')}
            with engine.begin() as conn:
                if 'pinned' not in cols:
                    conn.execute(text('ALTER TABLE notes ADD COLUMN pinned INTEGER DEFAULT 0'))
                if 'pin_x' not in cols:
                    conn.execute(text('ALTER TABLE notes ADD COLUMN pin_x INTEGER'))
                if 'pin_y' not in cols:
                    conn.execute(text('ALTER TABLE notes ADD COLUMN pin_y INTEGER'))
                if 'updated_at' not in cols:
                    conn.execute(text('ALTER TABLE notes ADD COLUMN updated_at DATETIME'))
    except Exception:
        pass


def init_db():
    import backend.models
    Base.metadata.create_all(bind=engine)
    _ensure_columns()
    # Seed the Featured Investigation library so the archive works immediately.
    try:
        from backend.seed import seed_featured_cases
        seed_featured_cases()
    except Exception:
        pass

@contextmanager
def get_db():
    try:
        yield db_session()
    finally:
        pass

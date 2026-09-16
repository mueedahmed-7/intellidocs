"""Lazy SQLAlchemy engine and explicit schema initialization."""
import os
from contextlib import contextmanager
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool
from backend.config import ENV_FILE
from backend.database.models import Base

# Importing backend.config loads the project-root .env before this module reads
# DATABASE_URL. This also makes `python -m backend.scripts.init_db` behave the
# same way as the FastAPI application.
_ = ENV_FILE

def database_url(environment=None):
    value = (os.environ if environment is None else environment).get("DATABASE_URL", "").strip()
    if not value:
        raise RuntimeError("Missing required configuration: DATABASE_URL.")
    return "postgresql+psycopg://" + value[len("postgresql://"):] if value.startswith("postgresql://") else value

_engine = _factory = None
def session_factory():
    global _engine, _factory
    if _factory is None:
        url = database_url(); kwargs = {"future": True}
        if url.startswith("sqlite"): kwargs.update(connect_args={"check_same_thread": False}, poolclass=StaticPool)
        _engine = create_engine(url, **kwargs); _factory = sessionmaker(_engine, expire_on_commit=False)
    return _factory
@contextmanager
def session_scope():
    session = session_factory()()
    try: yield session; session.commit()
    except Exception: session.rollback(); raise
    finally: session.close()
def init_database():
    """Create missing tables only; never drops or resets existing data."""
    engine = session_factory().kw["bind"]
    Base.metadata.create_all(engine)

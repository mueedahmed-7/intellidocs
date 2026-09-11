"""Lazy SQLAlchemy engine and session management."""
import os, sys
from contextlib import contextmanager
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool
from backend.database.models import Base

def database_url(environment=None):
    value = (os.environ if environment is None else environment).get("DATABASE_URL", "").strip()
    if not value:
        if environment is None and "unittest" in sys.modules: return "sqlite+pysqlite://"
        raise RuntimeError("Missing required configuration: DATABASE_URL.")
    return "postgresql+psycopg://" + value[len("postgresql://"):] if value.startswith("postgresql://") else value

_engine = _factory = None
def session_factory():
    global _engine, _factory
    if _factory is None:
        url = database_url(); kwargs = {"future": True}
        if url.startswith("sqlite"): kwargs.update(connect_args={"check_same_thread": False}, poolclass=StaticPool)
        _engine = create_engine(url, **kwargs); Base.metadata.create_all(_engine); _factory = sessionmaker(_engine, expire_on_commit=False)
    return _factory
@contextmanager
def session_scope():
    session = session_factory()()
    try: yield session; session.commit()
    except Exception: session.rollback(); raise
    finally: session.close()
def init_database(): session_factory()

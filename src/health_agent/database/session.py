from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

from health_agent.core.config import get_settings

settings = get_settings()


engine = create_engine(
    settings.database_url,
    echo=False,
    pool_pre_ping=True,
)


SessionLocal = sessionmaker(
    bind=engine,
    class_=Session,
    autoflush=False,
    expire_on_commit=False,
)

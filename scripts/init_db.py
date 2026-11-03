from sqlalchemy import text

from health_agent.database.base import Base
from health_agent.database.models import DocumentChunkModel  # noqa: F401
import health_agent.healthcare.models  # noqa: F401
from health_agent.database.session import engine


def main() -> None:
    with engine.begin() as connection:
        connection.execute(text("CREATE EXTENSION IF NOT EXISTS vector"))

    Base.metadata.create_all(bind=engine)

    print("Database initialized successfully.")


if __name__ == "__main__":
    main()

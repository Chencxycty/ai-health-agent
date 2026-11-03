from pathlib import Path

from alembic.config import Config

from alembic import command

PROJECT_ROOT = Path(__file__).resolve().parents[1]


def main() -> None:
    config = Config(str(PROJECT_ROOT / "alembic.ini"))
    command.upgrade(config, "head")

    print("Database migrated to the latest business schema.")


if __name__ == "__main__":
    main()

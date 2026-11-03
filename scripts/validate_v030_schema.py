"""Validate a v0.3.0 database before registering the Alembic baseline."""

import argparse
import json
from datetime import datetime
from pathlib import Path
from typing import Any

from alembic.autogenerate import compare_metadata
from alembic.config import Config
from alembic.migration import MigrationContext
from sqlalchemy import create_engine, inspect, text
from sqlalchemy.engine import Connection, make_url

from alembic import command
from health_agent.core.config import get_settings
from health_agent.database.base import Base
from health_agent.database.migration_scope import (
    MANAGED_TABLE_NAMES,
    include_business_object,
)

PROJECT_ROOT = Path(__file__).resolve().parents[1]


def database_target(database_url: str) -> str:
    url = make_url(database_url)
    host = url.host or "local"
    port = f":{url.port}" if url.port else ""
    database = f"/{url.database}" if url.database else ""
    return f"{url.drivername}://{host}{port}{database}"


def get_row_counts(connection: Connection) -> dict[str, int]:
    existing_tables = set(inspect(connection).get_table_names())
    quote = connection.dialect.identifier_preparer.quote
    counts: dict[str, int] = {}

    for table_name in sorted(MANAGED_TABLE_NAMES & existing_tables):
        statement = text(f"SELECT count(*) FROM {quote(table_name)}")
        counts[table_name] = int(connection.scalar(statement) or 0)

    return counts


def get_schema_differences(connection: Connection) -> list[Any]:
    context = MigrationContext.configure(
        connection,
        opts={
            "compare_type": True,
            "include_object": include_business_object,
        },
    )
    return compare_metadata(context, Base.metadata)


def validate(connection: Connection) -> dict[str, Any]:
    vector_installed = bool(
        connection.scalar(
            text("SELECT EXISTS (SELECT 1 FROM pg_extension WHERE extname = 'vector')")
        )
    )
    differences = get_schema_differences(connection)

    return {
        "vector_extension_installed": vector_installed,
        "schema_matches": vector_installed and not differences,
        "differences": [repr(item) for item in differences],
        "row_counts": get_row_counts(connection),
    }


def write_report(path: Path, report: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(report, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )


def main() -> None:
    parser = argparse.ArgumentParser(
        description=(
            "Compare an existing v0.3.0 database with the initial Alembic "
            "business schema. Stamping is refused if any difference exists."
        )
    )
    parser.add_argument(
        "--stamp",
        action="store_true",
        help="Register revision 20261103_0001 only after a clean comparison.",
    )
    parser.add_argument(
        "--report",
        type=Path,
        help="Optional path for the machine-readable validation report.",
    )
    args = parser.parse_args()

    settings = get_settings()
    engine = create_engine(settings.database_url, pool_pre_ping=True)

    with engine.connect() as connection:
        result = validate(connection)

    report: dict[str, Any] = {
        "captured_at": datetime.now().astimezone().isoformat(),
        "database": database_target(settings.database_url),
        "target_revision": "20261103_0001",
        **result,
        "stamped": False,
    }

    if args.stamp:
        if not result["schema_matches"]:
            report["stamp_error"] = (
                "Schema differs from the v0.3.0 baseline; no revision was stamped."
            )
        else:
            config = Config(str(PROJECT_ROOT / "alembic.ini"))
            command.stamp(config, "head")

            with engine.connect() as connection:
                counts_after = get_row_counts(connection)

            report["stamped"] = True
            report["row_counts_after_stamp"] = counts_after
            report["data_preserved"] = counts_after == result["row_counts"]

    if args.report:
        write_report(args.report, report)

    print(json.dumps(report, ensure_ascii=False, indent=2))

    if not result["schema_matches"] or (args.stamp and not report["stamped"]):
        raise SystemExit(1)


if __name__ == "__main__":
    main()

"""Objects managed by the application's Alembic migration history."""

from typing import Any

from health_agent.database import models as database_models  # noqa: F401
from health_agent.database.base import Base
from health_agent.healthcare import models as healthcare_models  # noqa: F401

MANAGED_TABLE_NAMES = frozenset(Base.metadata.tables)


def include_business_object(
    object_: Any,
    name: str | None,
    type_: str,
    reflected: bool,
    compare_to: Any,
) -> bool:
    """Keep autogenerate limited to business tables owned by this project.

    LangGraph checkpoint tables and any other SDK-owned tables deliberately
    remain outside this Alembic history.
    """
    if type_ == "table":
        return name in MANAGED_TABLE_NAMES

    table = getattr(object_, "table", None)
    if table is not None:
        return table.name in MANAGED_TABLE_NAMES

    return True

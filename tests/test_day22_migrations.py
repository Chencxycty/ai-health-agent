import importlib.util
from pathlib import Path
from types import SimpleNamespace

from health_agent.database.migration_scope import (
    MANAGED_TABLE_NAMES,
    include_business_object,
)

PROJECT_ROOT = Path(__file__).resolve().parents[1]
REVISION_PATH = (
    PROJECT_ROOT / "alembic" / "versions" / "20261103_0001_initial_business_schema.py"
)


class RecordingOperations:
    def __init__(self) -> None:
        self.calls: list[tuple] = []

    def execute(self, statement) -> None:
        self.calls.append(("execute", str(statement)))

    def create_table(self, name, *columns) -> None:
        self.calls.append(("create_table", name, columns))

    def create_index(self, name, table_name, columns, unique=False) -> None:
        self.calls.append(("create_index", name, table_name, tuple(columns), unique))

    def drop_index(self, name, table_name) -> None:
        self.calls.append(("drop_index", name, table_name))

    def drop_table(self, name) -> None:
        self.calls.append(("drop_table", name))


def load_revision():
    spec = importlib.util.spec_from_file_location(
        "day22_initial_revision", REVISION_PATH
    )
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_migration_scope_excludes_sdk_tables() -> None:
    assert MANAGED_TABLE_NAMES == {
        "document_chunks",
        "patients",
        "observations",
        "conditions",
    }
    assert include_business_object(None, "patients", "table", True, None)
    assert not include_business_object(None, "checkpoints", "table", True, None)
    assert not include_business_object(None, "checkpoint_writes", "table", True, None)

    checkpoint_column = SimpleNamespace(table=SimpleNamespace(name="checkpoints"))
    assert not include_business_object(
        checkpoint_column,
        "thread_id",
        "column",
        True,
        None,
    )


def test_initial_migration_creates_extension_before_business_tables() -> None:
    revision = load_revision()
    operations = RecordingOperations()
    revision.op = operations

    revision.upgrade()

    assert operations.calls[0] == (
        "execute",
        "CREATE EXTENSION IF NOT EXISTS vector",
    )
    created_tables = [call[1] for call in operations.calls if call[0] == "create_table"]
    assert created_tables == [
        "document_chunks",
        "patients",
        "conditions",
        "observations",
    ]
    assert not any("checkpoint" in str(call) for call in operations.calls)

    document_call = next(
        call
        for call in operations.calls
        if call[0] == "create_table" and call[1] == "document_chunks"
    )
    embedding_column = next(
        column
        for column in document_call[2]
        if getattr(column, "name", None) == "embedding"
    )
    assert str(embedding_column.type) == "VECTOR(1024)"


def test_downgrade_keeps_shared_vector_extension() -> None:
    revision = load_revision()
    operations = RecordingOperations()
    revision.op = operations

    revision.downgrade()

    dropped_tables = [call[1] for call in operations.calls if call[0] == "drop_table"]
    assert dropped_tables == [
        "observations",
        "conditions",
        "patients",
        "document_chunks",
    ]
    assert not any(call[0] == "execute" for call in operations.calls)

from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True)
class MCPToolInfo:
    name: str
    description: str
    input_schema: dict[str, Any]


@dataclass(frozen=True)
class MCPToolResult:
    name: str

    data: Any

    is_error: bool = False

    error: str | None = None

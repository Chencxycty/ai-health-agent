from health_agent.core.config import (
    get_settings,
)
from health_agent.mcp.client import (
    HealthMCPClient,
)


def main() -> None:
    settings = get_settings()

    client = HealthMCPClient(server_url=(settings.mcp_health_server_url))

    print("TOOLS")

    for tool in client.list_tools():
        print()
        print(tool.name)

        print(tool.description)

        print(tool.input_schema)

    print()
    print("CALL BMI")

    result = client.call_tool(
        name="calculate_bmi",
        arguments={
            "height_cm": 175,
            "weight_kg": 80,
        },
    )

    print(result)


if __name__ == "__main__":
    main()

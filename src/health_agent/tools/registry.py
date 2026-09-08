TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "calculate_bmi",
            "description": (
                "Calculate BMI from height in centimeters and weight in kilograms."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "height_cm": {
                        "type": "number",
                        "description": "Height in centimeters.",
                    },
                    "weight_kg": {
                        "type": "number",
                        "description": "Weight in kilograms.",
                    },
                },
                "required": [
                    "height_cm",
                    "weight_kg",
                ],
                "additionalProperties": False,
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "calculate_average_blood_pressure",
            "description": (
                "Calculate average systolic and diastolic "
                "blood pressure from multiple readings."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "readings": {
                        "type": "array",
                        "items": {
                            "type": "object",
                            "properties": {
                                "systolic": {
                                    "type": "number",
                                },
                                "diastolic": {
                                    "type": "number",
                                },
                            },
                            "required": [
                                "systolic",
                                "diastolic",
                            ],
                            "additionalProperties": False,
                        },
                    },
                },
                "required": ["readings"],
                "additionalProperties": False,
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "calculate_average_glucose",
            "description": (
                "Calculate the arithmetic mean of multiple blood glucose values."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "values": {
                        "type": "array",
                        "items": {
                            "type": "number",
                        },
                    },
                },
                "required": ["values"],
                "additionalProperties": False,
            },
        },
    },
]

from typing import Any

from health_agent.tools.health import (
    calculate_average_blood_pressure,
    calculate_average_glucose,
    calculate_bmi,
)
from health_agent.tools.schemas import (
    AverageBloodPressureInput,
    AverageGlucoseInput,
    BMIInput,
)


def execute_tool(
    name: str,
    arguments: dict[str, Any],
) -> Any:
    if name == "calculate_bmi":
        return calculate_bmi(BMIInput(**arguments))

    if name == "calculate_average_blood_pressure":
        return calculate_average_blood_pressure(AverageBloodPressureInput(**arguments))

    if name == "calculate_average_glucose":
        return calculate_average_glucose(AverageGlucoseInput(**arguments))

    raise ValueError(f"Unknown tool: {name}")

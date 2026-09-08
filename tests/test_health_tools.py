import pytest
from pydantic import ValidationError

from health_agent.tools.health import (
    calculate_average_blood_pressure,
    calculate_average_glucose,
    calculate_bmi,
)
from health_agent.tools.schemas import (
    AverageBloodPressureInput,
    AverageGlucoseInput,
    BloodPressureReading,
    BMIInput,
)


def test_calculate_bmi() -> None:
    result = calculate_bmi(
        BMIInput(
            height_cm=175,
            weight_kg=80,
        )
    )

    assert result == pytest.approx(
        26.12,
        rel=1e-2,
    )


def test_average_blood_pressure() -> None:
    data = AverageBloodPressureInput(
        readings=[
            BloodPressureReading(
                systolic=130,
                diastolic=80,
            ),
            BloodPressureReading(
                systolic=140,
                diastolic=90,
            ),
        ]
    )

    result = calculate_average_blood_pressure(data)

    assert result["average_systolic"] == 135
    assert result["average_diastolic"] == 85


def test_average_glucose() -> None:
    result = calculate_average_glucose(
        AverageGlucoseInput(
            values=[
                5.5,
                6.0,
                6.5,
            ]
        )
    )

    assert result == 6.0


def test_bmi_rejects_negative_height() -> None:
    with pytest.raises(ValidationError):
        BMIInput(
            height_cm=-175,
            weight_kg=80,
        )

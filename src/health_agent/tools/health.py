from health_agent.tools.schemas import (
    AverageBloodPressureInput,
    AverageGlucoseInput,
    BMIInput,
)


def calculate_bmi(data: BMIInput) -> float:
    """计算BMI（Body Mass Index，身体质量指数）。"""
    height_m = data.height_cm / 100

    bmi = data.weight_kg / (height_m**2)

    return round(bmi, 2)


def calculate_average_blood_pressure(
    data: AverageBloodPressureInput,
) -> dict[str, float]:
    """计算平均血压（收缩压和舒张压）。"""
    if not data.readings:
        raise ValueError("At least one blood pressure reading is required.")

    avg_systolic = sum(reading.systolic for reading in data.readings) / len(
        data.readings
    )

    avg_diastolic = sum(reading.diastolic for reading in data.readings) / len(
        data.readings
    )

    return {
        "average_systolic": round(avg_systolic, 2),
        "average_diastolic": round(avg_diastolic, 2),
    }


def calculate_average_glucose(
    data: AverageGlucoseInput,
) -> float:
    """计算平均血糖值。"""
    if not data.values:
        raise ValueError("At least one glucose value is required.")

    average = sum(data.values) / len(data.values)

    return round(average, 2)

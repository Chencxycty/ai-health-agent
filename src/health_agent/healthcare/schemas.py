from datetime import date, datetime
from typing import Literal

from pydantic import BaseModel, Field


class PatientCreate(BaseModel):
    patient_id: str = Field(
        min_length=1,
        max_length=64,
    )

    name: str

    gender: Literal[
        "male",
        "female",
        "other",
        "unknown",
    ]

    birth_date: date


class ObservationCreate(BaseModel):
    patient_id: str

    observation_type: Literal[
        "systolic_bp",
        "diastolic_bp",
        "glucose",
        "weight",
        "heart_rate",
    ]

    value: float

    unit: str

    observed_at: datetime


class ConditionCreate(BaseModel):
    patient_id: str

    code: str

    display: str

    status: Literal[
        "active",
        "inactive",
        "resolved",
    ] = "active"

    recorded_at: datetime

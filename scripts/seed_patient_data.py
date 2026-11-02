from datetime import (
    date,
    datetime,
    timezone,
)

from health_agent.database.session import (
    SessionLocal,
)
from health_agent.healthcare.repositories import (
    PatientRepository,
)
from health_agent.healthcare.schemas import (
    ConditionCreate,
    ObservationCreate,
    PatientCreate,
)


def main() -> None:
    with SessionLocal.begin() as session:
        repository = PatientRepository(session)

        existing = repository.get_patient("patient-demo-001")

        if existing is not None:
            print("Demo patient already exists.")
            return

        repository.create_patient(
            PatientCreate(
                patient_id=("patient-demo-001"),
                name="Demo Patient",
                gender="male",
                birth_date=date(
                    1990,
                    1,
                    1,
                ),
            )
        )

        blood_pressures = [
            (
                datetime(
                    2026,
                    10,
                    1,
                    8,
                    0,
                    tzinfo=timezone.utc,
                ),
                132,
                82,
            ),
            (
                datetime(
                    2026,
                    10,
                    2,
                    8,
                    0,
                    tzinfo=timezone.utc,
                ),
                136,
                84,
            ),
            (
                datetime(
                    2026,
                    10,
                    3,
                    8,
                    0,
                    tzinfo=timezone.utc,
                ),
                130,
                80,
            ),
        ]

        for (
            observed_at,
            systolic,
            diastolic,
        ) in blood_pressures:
            repository.add_observation(
                ObservationCreate(
                    patient_id=("patient-demo-001"),
                    observation_type=("systolic_bp"),
                    value=systolic,
                    unit="mmHg",
                    observed_at=observed_at,
                )
            )

            repository.add_observation(
                ObservationCreate(
                    patient_id=("patient-demo-001"),
                    observation_type=("diastolic_bp"),
                    value=diastolic,
                    unit="mmHg",
                    observed_at=observed_at,
                )
            )

        repository.add_condition(
            ConditionCreate(
                patient_id=("patient-demo-001"),
                code="demo-hypertension",
                display="Hypertension",
                status="active",
                recorded_at=datetime.now(timezone.utc),
            )
        )

    print("Demo patient data inserted.")


if __name__ == "__main__":
    main()

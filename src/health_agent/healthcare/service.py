from datetime import datetime

from health_agent.database.session import (
    SessionLocal,
)
from health_agent.healthcare.repositories import (
    PatientRepository,
)


class PatientDataService:
    def get_patient_summary(
        self,
        patient_id: str,
    ) -> dict:
        with SessionLocal() as session:
            repository = PatientRepository(session)

            patient = repository.get_patient(patient_id)

            if patient is None:
                raise ValueError("Patient not found.")

            observations = repository.list_observations(
                patient_id=patient_id,
                limit=20,
            )

            conditions = repository.list_conditions(patient_id)

        return {
            "patient": {
                "patient_id": patient.patient_id,
                "name": patient.name,
                "gender": patient.gender,
                "birth_date": patient.birth_date.isoformat(),
            },
            "observations": [
                {
                    "type": item.observation_type,
                    "value": item.value,
                    "unit": item.unit,
                    "observed_at": item.observed_at.isoformat(),
                }
                for item in observations
            ],
            "conditions": [
                {
                    "code": item.code,
                    "display": item.display,
                    "status": item.status,
                }
                for item in conditions
            ],
        }

    def get_observations(
        self,
        patient_id: str,
        observation_type: str | None = None,
        start_at: datetime | None = None,
    ) -> list[dict]:
        with SessionLocal() as session:
            repository = PatientRepository(session)

            models = repository.list_observations(
                patient_id=patient_id,
                observation_type=(observation_type),
                start_at=start_at,
            )

        return [
            {
                "type": model.observation_type,
                "value": model.value,
                "unit": model.unit,
                "observed_at": model.observed_at.isoformat(),
            }
            for model in models
        ]


from health_agent.healthcare.fhir import (
    condition_to_fhir,
    observation_to_fhir,
    patient_to_fhir,
)


class FHIRService:
    def get_patient_bundle(
        self,
        patient_id: str,
    ) -> dict:
        with SessionLocal() as session:
            repository = PatientRepository(session)

            patient = repository.get_patient(patient_id)

            if patient is None:
                raise ValueError("Patient not found.")

            observations = repository.list_observations(patient_id)

            conditions = repository.list_conditions(patient_id)

        resources = [
            patient_to_fhir(patient),
            *[observation_to_fhir(item) for item in observations],
            *[condition_to_fhir(item) for item in conditions],
        ]

        return {
            "resourceType": "Bundle",
            "type": "collection",
            "total": len(resources),
            "entry": [{"resource": resource} for resource in resources],
        }

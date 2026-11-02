from health_agent.healthcare.models import (
    ConditionModel,
    ObservationModel,
    PatientModel,
)


FHIR_OBSERVATION_CODES = {
    "systolic_bp": {
        "system": "http://loinc.org",
        "code": "8480-6",
        "display": "Systolic blood pressure",
    },
    "diastolic_bp": {
        "system": "http://loinc.org",
        "code": "8462-4",
        "display": "Diastolic blood pressure",
    },
    "body_weight": {
        "system": "http://loinc.org",
        "code": "29463-7",
        "display": "Body weight",
    },
}


def patient_to_fhir(
    patient: PatientModel,
) -> dict:
    return {
        "resourceType": "Patient",
        "id": patient.patient_id,
        "name": [
            {
                "text": patient.name,
            }
        ],
        "gender": patient.gender,
        "birthDate": patient.birth_date.isoformat(),
    }


def observation_to_fhir(
    observation: ObservationModel,
) -> dict:
    code = FHIR_OBSERVATION_CODES.get(
        observation.observation_type,
        {
            "system": "urn:health-agent:observation-type",
            "code": observation.observation_type,
            "display": observation.observation_type,
        },
    )

    return {
        "resourceType": "Observation",
        "id": str(observation.id),
        "status": "final",
        "code": {"coding": [code]},
        "subject": {"reference": (f"Patient/{observation.patient_id}")},
        "effectiveDateTime": observation.observed_at.isoformat(),
        "valueQuantity": {
            "value": observation.value,
            "unit": observation.unit,
        },
    }


def condition_to_fhir(
    condition: ConditionModel,
) -> dict:
    return {
        "resourceType": "Condition",
        "id": str(condition.id),
        "clinicalStatus": {
            "coding": [
                {
                    "system": (
                        "http://terminology.hl7.org/CodeSystem/condition-clinical"
                    ),
                    "code": condition.status,
                }
            ]
        },
        "code": {
            "coding": [
                {
                    "system": "urn:health-agent:condition",
                    "code": condition.code,
                    "display": condition.display,
                }
            ]
        },
        "subject": {"reference": (f"Patient/{condition.patient_id}")},
        "recordedDate": condition.recorded_at.isoformat(),
    }

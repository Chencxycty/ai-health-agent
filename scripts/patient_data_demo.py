from pprint import pprint

from health_agent.healthcare.service import (
    PatientDataService,
)


def main() -> None:
    service = PatientDataService()

    result = service.get_patient_summary("patient-demo-001")

    pprint(result)


if __name__ == "__main__":
    main()

import json

from health_agent.healthcare.service import (
    FHIRService,
)


def main() -> None:
    service = FHIRService()

    bundle = service.get_patient_bundle("patient-demo-001")

    print(
        json.dumps(
            bundle,
            ensure_ascii=False,
            indent=2,
        )
    )


if __name__ == "__main__":
    main()

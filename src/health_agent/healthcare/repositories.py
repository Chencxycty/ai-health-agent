from datetime import datetime

from sqlalchemy import select
from sqlalchemy.orm import Session

from health_agent.healthcare.models import (
    ConditionModel,
    ObservationModel,
    PatientModel,
)
from health_agent.healthcare.schemas import (
    ConditionCreate,
    ObservationCreate,
    PatientCreate,
)


class PatientRepository:
    def __init__(
        self,
        session: Session,
    ) -> None:
        self.session = session

    def create_patient(
        self,
        data: PatientCreate,
    ) -> PatientModel:
        patient = PatientModel(**data.model_dump())

        self.session.add(patient)
        self.session.flush()

        return patient

    def get_patient(
        self,
        patient_id: str,
    ) -> PatientModel | None:
        statement = select(PatientModel).where(PatientModel.patient_id == patient_id)

        return self.session.scalar(statement)

    def add_observation(
        self,
        data: ObservationCreate,
    ) -> ObservationModel:
        model = ObservationModel(**data.model_dump())

        self.session.add(model)
        self.session.flush()

        return model

    def list_observations(
        self,
        patient_id: str,
        observation_type: str | None = None,
        start_at: datetime | None = None,
        limit: int = 100,
    ) -> list[ObservationModel]:
        statement = select(ObservationModel).where(
            ObservationModel.patient_id == patient_id
        )

        if observation_type:
            statement = statement.where(
                ObservationModel.observation_type == observation_type
            )

        if start_at:
            statement = statement.where(ObservationModel.observed_at >= start_at)

        statement = statement.order_by(ObservationModel.observed_at.desc()).limit(limit)

        return list(self.session.scalars(statement).all())

    def add_condition(
        self,
        data: ConditionCreate,
    ) -> ConditionModel:
        model = ConditionModel(**data.model_dump())

        self.session.add(model)
        self.session.flush()

        return model

    def list_conditions(
        self,
        patient_id: str,
    ) -> list[ConditionModel]:
        statement = (
            select(ConditionModel)
            .where(ConditionModel.patient_id == patient_id)
            .order_by(ConditionModel.recorded_at.desc())
        )

        return list(self.session.scalars(statement).all())

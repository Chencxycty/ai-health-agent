from sqlalchemy import select
from sqlalchemy.orm import Session

from health_agent.database.models import (
    DocumentChunkModel,
)


class DocumentChunkRepository:
    def __init__(
        self,
        session: Session,
    ) -> None:
        self.session = session

    def vector_search(
        self,
        query_embedding: list[float],
        top_k: int = 5,
    ) -> list[tuple[DocumentChunkModel, float]]:
        distance = DocumentChunkModel.embedding.cosine_distance(query_embedding)

        statement = (
            select(
                DocumentChunkModel,
                distance.label("distance"),
            )
            .order_by(distance)
            .limit(top_k)
        )

        rows = self.session.execute(statement).all()

        return [
            (
                row[0],
                1.0 - float(row[1]),
            )
            for row in rows
        ]

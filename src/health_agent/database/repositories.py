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
        document_id: str | None = None,
    ) -> list[tuple[DocumentChunkModel, float]]:
        """使用向量搜索查找与查询嵌入最相似的文档块。(一般需要先做metadata filter)"""
        distance = DocumentChunkModel.embedding.cosine_distance(query_embedding)

        statement = select(
            DocumentChunkModel,
            distance.label("distance"),
        )

        if document_id is not None:
            statement = statement.where(DocumentChunkModel.document_id == document_id)

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

    def get_all(
        self,
    ) -> list[DocumentChunkModel]:
        """获取所有文档块。"""
        statement = select(DocumentChunkModel).order_by(DocumentChunkModel.id)

        return list(self.session.scalars(statement).all())

import json

import numpy as np

from health_agent.database.models import (
    DocumentChunkModel,
)
from health_agent.database.session import SessionLocal


def main() -> None:
    with open(
        "data/processed/chunks.json",
        encoding="utf-8",
    ) as file:
        raw_chunks = json.load(file)

    embeddings = np.load("data/processed/embeddings.npy")

    if len(raw_chunks) != len(embeddings):
        raise ValueError("Chunk count does not match embedding count.")

    with SessionLocal.begin() as session:
        for raw_chunk, embedding in zip(
            raw_chunks,
            embeddings,
            strict=True,
        ):
            model = DocumentChunkModel(
                chunk_id=raw_chunk["chunk_id"],
                document_id=raw_chunk["document_id"],
                title=raw_chunk["title"],
                source=raw_chunk["source"],
                page=raw_chunk["page"],
                chunk_index=raw_chunk["chunk_index"],
                content=raw_chunk["content"],
                embedding=embedding.tolist(),
            )

            session.add(model)

    print(f"Inserted {len(raw_chunks)} chunks.")


if __name__ == "__main__":
    main()

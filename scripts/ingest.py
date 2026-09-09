import json
from dataclasses import asdict
from pathlib import Path

import numpy as np

from health_agent.rag.chunker import chunk_document
from health_agent.rag.embeddings import EmbeddingModel
from health_agent.rag.loader import load_pdf


def main() -> None:
    pdf_path = Path("data/raw/hypertension_standard.pdf")

    pages = load_pdf(
        file_path=pdf_path,
        title="基层医疗卫生机构高血压防治管理标准",
    )

    chunks = chunk_document(
        pages=pages,
        chunk_size=700,
        overlap=120,
    )

    with open(
        "data/processed/chunks.json",
        "w",
        encoding="utf-8",
    ) as file:
        json.dump(
            [asdict(chunk) for chunk in chunks],
            file,
            ensure_ascii=False,
            indent=2,
        )

    model = EmbeddingModel(model_name="BAAI/bge-m3")

    texts = [chunk.content for chunk in chunks]

    embeddings = model.embed_documents(texts)

    print(f"Pages: {len(pages)}")

    print(f"Chunks: {len(chunks)}")

    print(f"Embedding dimension: {model.dimension}")

    np.save(
        "data/processed/embeddings.npy",
        embeddings,
    )


if __name__ == "__main__":
    main()

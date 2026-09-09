import json

import numpy as np

from health_agent.rag.embeddings import EmbeddingModel
from health_agent.rag.schemas import DocumentChunk
from health_agent.rag.search import cosine_search


def main() -> None:
    with open(
        "data/processed/chunks.json",
        encoding="utf-8",
    ) as file:
        raw_chunks = json.load(file)

    chunks = [DocumentChunk(**item) for item in raw_chunks]

    document_embeddings = np.load("data/processed/embeddings.npy")

    model = EmbeddingModel(model_name="BAAI/bge-m3")

    queries = [
        "高血压患者家庭血压监测有哪些要求？",
        "高血压患者应该如何进行随访？",
        "哪些情况需要进行转诊？",
        "高血压患者健康教育包括哪些内容？",
        "基层医疗机构需要配备哪些血压测量设备？",
        "高血压患者需要进行哪些检查？",
        "血压控制不满意时应该怎么办？",
        "高血压管理的基本要求是什么？",
        "家庭血压测量需要注意什么？",
        "高血压患者药物治疗管理有哪些要求？",
    ]

    for query in queries:
        query_embedding = model.embed_query(query)

        results = cosine_search(
            query_embedding=query_embedding,
            document_embeddings=document_embeddings,
            chunks=chunks,
            top_k=5,
        )

        print(f"\nQuery: {query}\n")

        for index, result in enumerate(
            results,
            start=1,
        ):
            print(f"[{index}] score={result.score:.4f} page={result.chunk.page}")

            print(result.chunk.content[:300])

            print("-" * 80)


if __name__ == "__main__":
    main()

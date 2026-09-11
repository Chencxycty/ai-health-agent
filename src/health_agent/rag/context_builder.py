from health_agent.rag.schemas import (
    SearchResult,
)


def build_context(
    results: list[SearchResult],
) -> str:
    """根据检索结果构建上下文字符串。"""
    blocks: list[str] = []

    for index, result in enumerate(
        results,
        start=1,
    ):
        chunk = result.chunk

        block = (
            f"[Source {index}]\n"
            f"Title: {chunk.title}\n"
            f"Page: {chunk.page}\n"
            f"Chunk ID: {chunk.chunk_id}\n"
            f"Content:\n"
            f"{chunk.content}"
        )

        blocks.append(block)

    return "\n\n".join(blocks)

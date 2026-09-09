from pathlib import Path
from uuid import uuid4

from pypdf import PdfReader

from health_agent.rag.schemas import PageDocument


def clean_text(text: str) -> str:
    return " ".join(text.split())


def load_pdf(
    file_path: Path,
    title: str | None = None,
    source: str | None = None,
) -> list[PageDocument]:
    """从PDF文件中加载文本内容，并将“每一页”的内容封装为PageDocument对象。"""
    reader = PdfReader(file_path)

    document_id = str(uuid4())

    document_title = title or file_path.stem
    document_source = source or str(file_path)

    pages: list[PageDocument] = []

    for page_index, page in enumerate(reader.pages):
        raw_text = page.extract_text() or ""
        content = clean_text(raw_text)

        if not content:
            continue

        pages.append(
            PageDocument(
                document_id=document_id,
                title=document_title,
                source=document_source,
                page=page_index + 1,
                content=content,
            )
        )

    return pages

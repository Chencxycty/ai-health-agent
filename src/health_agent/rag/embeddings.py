import numpy as np
from sentence_transformers import SentenceTransformer


class EmbeddingModel:
    def __init__(
        self,
        model_name: str,
    ) -> None:
        """初始化嵌入模型，加载指定名称的SentenceTransformer模型。"""
        self.model = SentenceTransformer(model_name)

    @property
    def dimension(self) -> int:
        """获取嵌入向量的维度。"""
        return self.model.get_sentence_embedding_dimension()

    def embed_documents(
        self,
        texts: list[str],
    ) -> np.ndarray:
        """将多个文本转换为嵌入向量。"""
        return self.model.encode(
            texts,
            normalize_embeddings=True,
            show_progress_bar=True,
        )

    def embed_query(
        self,
        query: str,
    ) -> np.ndarray:
        """将查询文本转换为嵌入向量。"""
        result = self.model.encode(
            [query],
            normalize_embeddings=True,
        )

        return result[0]

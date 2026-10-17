from uuid import UUID

import chromadb
from fastembed import TextEmbedding
from langchain_chroma import Chroma
from langchain_core.embeddings import Embeddings

from app.core.config import get_settings


class FastEmbedEmbeddings(Embeddings):
    def __init__(self, cache_dir: str) -> None:
        self._model = TextEmbedding(
            model_name="BAAI/bge-small-en-v1.5",
            cache_dir=cache_dir,
            lazy_load=True,
        )

    def embed_documents(self, texts: list[str]) -> list[list[float]]:
        return [[float(value) for value in vector] for vector in self._model.embed(texts)]

    def embed_query(self, text: str) -> list[float]:
        vector = next(self._model.query_embed(text))
        return [float(value) for value in vector]


def get_school_vector_store(school_id: UUID) -> Chroma:
    settings = get_settings()
    if settings.chroma_host:
        client = chromadb.HttpClient(
            host=settings.chroma_host,
            port=settings.chroma_port,
        )
    else:
        client = chromadb.PersistentClient(path=settings.chroma_persist_directory)

    return Chroma(
        client=client,
        collection_name=f"school_{school_id.hex}",
        embedding_function=FastEmbedEmbeddings(cache_dir=settings.embedding_cache_directory),
        create_collection_if_not_exists=True,
    )

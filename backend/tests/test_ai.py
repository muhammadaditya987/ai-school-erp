from pathlib import Path
from types import SimpleNamespace
from uuid import uuid4

import pytest
from pydantic import SecretStr

import app.ai.agent as agent
import app.ai.ingestion as ingestion
import app.ai.providers as providers
import app.core.storage as storage
from app.core.config import Settings


@pytest.mark.parametrize(
    ("provider", "settings", "expected_class"),
    [
        ("openai", {"ai_api_key": SecretStr("test-openai-key")}, "ChatOpenAI"),
        ("gemini", {"gemini_api_key": SecretStr("test-gemini-key")}, "ChatGoogleGenerativeAI"),
        ("ollama", {}, "ChatOllama"),
        (
            "huggingface",
            {"huggingface_api_token": SecretStr("test-huggingface-token")},
            "ChatHuggingFace",
        ),
    ],
)
def test_ai_provider_adapters_build_the_selected_model(
    provider: str,
    settings: dict[str, object],
    expected_class: str,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(
        providers,
        "get_settings",
        lambda: Settings(ai_provider=provider, **settings),
    )

    model = providers.create_chat_model()

    assert type(model).__name__ == expected_class


def test_cloud_ai_providers_require_a_secret(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(
        providers,
        "get_settings",
        lambda: Settings(ai_provider="openai"),
    )

    with pytest.raises(RuntimeError, match="Set AI_API_KEY"):
        providers.create_chat_model()

    monkeypatch.setattr(
        providers,
        "get_settings",
        lambda: Settings(ai_provider="openai", ai_api_key=SecretStr("")),
    )
    with pytest.raises(RuntimeError, match="Set AI_API_KEY"):
        providers.create_chat_model()


def test_managed_postgres_urls_are_normalized_for_async_sqlalchemy() -> None:
    settings = Settings(database_url="postgres://school:secret@db.example/school")

    assert settings.database_url == "postgresql+asyncpg://school:secret@db.example/school"


def test_agent_does_not_call_a_model_when_the_school_has_no_documents(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    school_id = uuid4()
    empty_collection = SimpleNamespace(_collection=SimpleNamespace(count=lambda: 0))
    monkeypatch.setattr(agent, "get_school_vector_store", lambda _school_id: empty_collection)
    monkeypatch.setattr(
        agent,
        "create_chat_model",
        lambda: pytest.fail("the model must not run without indexed school evidence"),
    )

    result = agent.ask_school_agent(school_id, "What is the school policy?")

    assert "Belum ada dokumen" in result["answer"]


def test_each_school_gets_a_separate_chroma_collection(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    from langchain_core.embeddings import Embeddings

    import app.ai.vector_store as vector_store

    class FakeEmbeddings(Embeddings):
        def embed_documents(self, texts: list[str]) -> list[list[float]]:
            return [[0.0, 0.0] for _ in texts]

        def embed_query(self, text: str) -> list[float]:
            return [0.0, 0.0]

    monkeypatch.setattr(
        vector_store,
        "get_settings",
        lambda: Settings(chroma_persist_directory=str(tmp_path)),
    )
    monkeypatch.setattr(vector_store, "FastEmbedEmbeddings", lambda **_kwargs: FakeEmbeddings())
    first_school, second_school = uuid4(), uuid4()

    first_collection = vector_store.get_school_vector_store(first_school)
    second_collection = vector_store.get_school_vector_store(second_school)

    assert first_collection._collection.name == f"school_{first_school.hex}"
    assert second_collection._collection.name == f"school_{second_school.hex}"
    assert first_collection._collection.name != second_collection._collection.name


def test_llamaindex_parser_chunks_documents_before_chroma_ingestion(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    from llama_index.core.schema import Document as LlamaDocument

    indexed: list = []
    monkeypatch.setattr(
        ingestion,
        "SimpleDirectoryReader",
        lambda input_files: SimpleNamespace(
            load_data=lambda: [
                LlamaDocument(
                    text="School policy. " * 300,
                    metadata={"page_label": "1"},
                )
            ]
        ),
    )
    monkeypatch.setattr(
        ingestion,
        "get_school_vector_store",
        lambda _school_id: SimpleNamespace(add_documents=indexed.extend),
    )

    school_id = uuid4()
    count = ingestion.index_school_document(school_id, "guide.md", b"school policy")

    assert count == len(indexed)
    assert count > 1
    assert all(item.metadata["school_id"] == str(school_id) for item in indexed)
    assert all(item.metadata["source"] == "guide.md" for item in indexed)


def test_s3_storage_adapter_uploads_and_reads_objects(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    from moto import mock_aws

    settings = SimpleNamespace(
        s3_endpoint_url=None,
        s3_region="us-east-1",
        s3_access_key_id=SecretStr("test-access-key"),
        s3_secret_access_key=SecretStr("test-secret-key"),
        s3_bucket="school-documents",
    )
    monkeypatch.setattr(storage, "get_settings", lambda: settings)
    storage.get_s3_client.cache_clear()
    try:
        with mock_aws():
            storage.get_s3_client().create_bucket(Bucket=settings.s3_bucket)
            storage.put_object("schools/a/guide.md", b"safe school data", "text/plain")

            assert storage.get_object("schools/a/guide.md") == b"safe school data"
    finally:
        storage.get_s3_client.cache_clear()

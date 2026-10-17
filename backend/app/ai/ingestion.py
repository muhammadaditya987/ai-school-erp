import tempfile
from pathlib import Path
from uuid import UUID

from langchain_core.documents import Document
from llama_index.core import SimpleDirectoryReader
from llama_index.core.node_parser import SentenceSplitter

from app.ai.vector_store import get_school_vector_store


def index_school_document(school_id: UUID, filename: str, content: bytes) -> int:
    with tempfile.TemporaryDirectory(prefix="school-erp-ingest-") as directory:
        file_path = Path(directory) / Path(filename).name
        file_path.write_bytes(content)
        llama_documents = SimpleDirectoryReader(input_files=[str(file_path)]).load_data()

    documents = [
        Document(
            page_content=document.text,
            metadata={
                "school_id": str(school_id),
                "source": Path(filename).name,
                "page": document.metadata.get("page_label", str(index + 1)),
            },
        )
        for index, document in enumerate(llama_documents)
        if document.text.strip()
    ]
    if not documents:
        raise ValueError("The uploaded document does not contain readable text")

    splitter = SentenceSplitter(chunk_size=700, chunk_overlap=100)
    chunks = [
        Document(page_content=chunk, metadata=document.metadata)
        for document in documents
        for chunk in splitter.split_text(document.page_content)
    ]
    get_school_vector_store(school_id).add_documents(chunks)
    return len(chunks)

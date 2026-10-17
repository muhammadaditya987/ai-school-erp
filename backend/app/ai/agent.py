from typing import TypedDict
from uuid import UUID

from langchain_core.tools import tool
from langgraph.prebuilt import create_react_agent

from app.ai.providers import create_chat_model
from app.ai.vector_store import get_school_vector_store
from app.core.config import get_settings


class AnswerState(TypedDict):
    answer: str
    provider: str


def ask_school_agent(school_id: UUID, question: str) -> dict[str, str]:
    vector_store = get_school_vector_store(school_id)
    if vector_store._collection.count() == 0:
        return {
            "answer": "Belum ada dokumen sekolah yang selesai diindeks.",
            "provider": get_settings().ai_provider,
        }

    @tool
    def search_school_documents(search_query: str) -> str:
        """Search only the authenticated school's indexed documents for relevant facts."""
        matches = vector_store.similarity_search(search_query, k=4)
        if not matches:
            return "No school documents have been indexed yet."
        return "\n\n".join(
            f"Source: {item.metadata.get('source', 'school document')}\n{item.page_content}"
            for item in matches
        )

    agent = create_react_agent(
        create_chat_model(),
        [search_school_documents],
        prompt=(
            "You are a careful school ERP assistant. Use search_school_documents before "
            "answering questions about school records. Only use information belonging to "
            "the current school. If the documents do not contain the answer, say so instead "
            "of inventing facts. Never expose another school's information."
        ),
    )
    result = agent.invoke({"messages": [{"role": "user", "content": question}]})
    content = result["messages"][-1].content
    answer = content if isinstance(content, str) else str(content)
    return {"answer": answer, "provider": get_settings().ai_provider}

import asyncio

from mcp.server.fastmcp import FastMCP
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine

from app.ai.vector_store import get_school_vector_store
from app.api.auth import authenticate_access_token
from app.core.config import get_settings
from app.db.models import UserRole

mcp = FastMCP("School ERP knowledge search")


@mcp.tool()
async def search_school_knowledge(query: str) -> str:
    """Search the authenticated user's school documents using the configured short-lived JWT."""
    if len(query.strip()) < 3 or len(query) > 1000:
        raise ValueError("The search query must be between 3 and 1000 characters")
    access_token = get_settings().mcp_access_token
    if access_token is None or not access_token.get_secret_value().strip():
        raise RuntimeError("Set MCP_ACCESS_TOKEN in the MCP server environment")

    engine = create_async_engine(get_settings().database_url, pool_pre_ping=True)
    try:
        async with async_sessionmaker(engine, expire_on_commit=False)() as session:
            user = await authenticate_access_token(
                access_token.get_secret_value(),
                session,
            )
            if user.role not in {UserRole.SCHOOL_ADMIN, UserRole.TEACHER}:
                raise ValueError("This role cannot search school knowledge documents")
            school_id = user.school_id
    finally:
        await engine.dispose()

    matches = await asyncio.to_thread(
        get_school_vector_store(school_id).similarity_search,
        query,
        4,
    )
    if not matches:
        return "No matching school documents were found."
    return "\n\n".join(
        f"Source: {item.metadata.get('source', 'school document')}\n{item.page_content}"
        for item in matches
    )


if __name__ == "__main__":
    mcp.run(transport="stdio")

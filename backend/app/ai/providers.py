from langchain_core.language_models import BaseChatModel

from app.core.config import get_settings


def create_chat_model() -> BaseChatModel:
    settings = get_settings()
    provider = settings.ai_provider.casefold()

    if provider == "openai":
        if not settings.ai_api_key or not settings.ai_api_key.get_secret_value().strip():
            raise RuntimeError("Set AI_API_KEY before using the OpenAI provider")
        from langchain_openai import ChatOpenAI

        return ChatOpenAI(
            model=settings.ai_model,
            api_key=settings.ai_api_key.get_secret_value(),
            timeout=60,
            max_retries=2,
        )
    if provider == "gemini":
        if not settings.gemini_api_key or not settings.gemini_api_key.get_secret_value().strip():
            raise RuntimeError("Set GEMINI_API_KEY before using the Gemini provider")
        from langchain_google_genai import ChatGoogleGenerativeAI

        return ChatGoogleGenerativeAI(
            model=settings.gemini_model,
            google_api_key=settings.gemini_api_key.get_secret_value(),
            max_retries=2,
        )
    if provider == "ollama":
        from langchain_ollama import ChatOllama

        return ChatOllama(
            model=settings.ollama_model,
            base_url=settings.ollama_base_url,
            temperature=0,
        )
    if provider == "huggingface":
        if (
            not settings.huggingface_api_token
            or not settings.huggingface_api_token.get_secret_value().strip()
        ):
            raise RuntimeError(
                "Set HUGGINGFACE_API_TOKEN before using the HuggingFace provider"
            )
        from langchain_huggingface import ChatHuggingFace, HuggingFaceEndpoint

        endpoint = HuggingFaceEndpoint(
            repo_id=settings.huggingface_model,
            task="text-generation",
            huggingfacehub_api_token=settings.huggingface_api_token.get_secret_value(),
            max_new_tokens=512,
            timeout=60,
        )
        return ChatHuggingFace(llm=endpoint)

    raise RuntimeError(f"Unsupported AI provider: {provider}")

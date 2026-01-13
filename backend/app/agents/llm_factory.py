"""LLM factory for creating language model instances."""
from langchain_openai import ChatOpenAI
from langchain_google_genai import ChatGoogleGenerativeAI

from app.config import settings


class LLMFactory:
    """Factory for creating LLM instances based on configuration."""

    @staticmethod
    def create_llm(temperature: float = 0.0):
        """
        Create an LLM instance based on the configured provider.

        Args:
            temperature: Temperature for response generation (0.0 = deterministic)

        Returns:
            LLM instance configured for the specified provider

        Raises:
            ValueError: If the provider is not supported
        """
        provider = settings.llm_provider.lower()

        if provider == "openai":
            if not settings.openai_api_key:
                raise ValueError("OPENAI_API_KEY not configured")
            return ChatOpenAI(
                model=settings.llm_model,
                temperature=temperature,
                api_key=settings.openai_api_key,
            )

        elif provider == "gemini":
            if not settings.google_api_key:
                raise ValueError("GOOGLE_API_KEY not configured")
            return ChatGoogleGenerativeAI(
                model=settings.llm_model,
                temperature=temperature,
                google_api_key=settings.google_api_key,
            )

        elif provider == "ollama":
            # For Ollama, we use ChatOpenAI with a local base URL
            from langchain_community.chat_models import ChatOllama

            return ChatOllama(
                model=settings.llm_model,
                temperature=temperature,
            )

        else:
            raise ValueError(
                f"Unsupported LLM provider: {provider}. "
                f"Supported providers: openai, gemini, ollama"
            )


# Convenience function
def get_llm(temperature: float = 0.0):
    """Get an LLM instance with the specified temperature."""
    return LLMFactory.create_llm(temperature=temperature)

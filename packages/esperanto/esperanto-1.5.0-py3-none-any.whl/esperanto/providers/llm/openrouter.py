"""OpenRouter language model implementation."""

import os
from dataclasses import dataclass
from typing import TYPE_CHECKING, Any, Dict, List, Optional  # Added Optional

from openai import AsyncOpenAI, OpenAI

from esperanto.common_types import Model
from esperanto.providers.llm.openai import OpenAILanguageModel

if TYPE_CHECKING:
    from langchain_openai import ChatOpenAI


@dataclass
class OpenRouterLanguageModel(OpenAILanguageModel):
    """OpenRouter language model implementation using OpenAI-compatible API."""

    base_url: Optional[str] = None  # Changed type hint
    api_key: Optional[str] = None  # Changed type hint

    def __post_init__(self):
        # Initialize OpenRouter-specific configuration
        self.base_url = self.base_url or os.getenv(
            "OPENROUTER_BASE_URL", "https://openrouter.ai/api/v1"
        )
        self.api_key = self.api_key or os.getenv("OPENROUTER_API_KEY")

        if not self.api_key:
            raise ValueError(
                "OpenRouter API key not found. Set the OPENROUTER_API_KEY environment variable."
            )

        # Call parent's post_init to set up normalized response handling
        super().__post_init__()

        # Initialize OpenAI clients with OpenRouter configuration
        self.client = OpenAI(
            api_key=self.api_key,
            base_url=self.base_url,
            organization=self.organization,
        )
        self.async_client = AsyncOpenAI(
            api_key=self.api_key,
            base_url=self.base_url,
            organization=self.organization,
        )

    def _get_api_kwargs(self, exclude_stream: bool = False) -> Dict[str, Any]:
        """Get kwargs for API calls, filtering out provider-specific args.

        Note: OpenRouter doesn't support JSON response format for non-OpenAI models.
        """
        kwargs = super()._get_api_kwargs(exclude_stream)

        # Remove response_format for non-OpenAI models
        model = self.get_model_name().lower()
        if "response_format" in kwargs and not model.startswith(("openai/", "gpt-")):
            kwargs.pop("response_format")

        return kwargs

    def _get_default_model(self) -> str:
        """Get the default model name."""
        return "anthropic/claude-2"

    @property
    def provider(self) -> str:
        """Get the provider name."""
        return "openrouter"

    @property
    def models(self) -> List[Model]:
        """List all available models for this provider."""
        models = self.client.models.list()
        return [
            Model(
                id=model.id,
                owned_by=model.id.split("/")[0] if "/" in model.id else "OpenRouter",
                context_window=getattr(model, "context_window", None),
                type="language",
            )
            for model in models
            if not any(
                model.id.startswith(prefix)
                for prefix in [
                    "text-embedding",  # Exclude embedding models
                    "whisper",  # Exclude speech models
                    "tts",  # Exclude text-to-speech models
                ]
            )
        ]

    def to_langchain(self) -> "ChatOpenAI":
        """Convert to a LangChain chat model.

        Raises:
            ImportError: If langchain_openai is not installed.
        """
        try:
            from langchain_openai import ChatOpenAI
        except ImportError as e:
            raise ImportError(
                "Langchain integration requires langchain_openai. "
                "Install with: uv add esperanto[openrouter,langchain] or pip install esperanto[openrouter,langchain]"
            ) from e

        model_kwargs = {}
        if self.structured and isinstance(self.structured, dict):
            structured_type = self.structured.get("type")
            if structured_type in [
                "json",
                "json_object",
            ] and self.get_model_name().lower().startswith(("openai/", "gpt-")):
                model_kwargs["response_format"] = {"type": "json_object"}

        langchain_kwargs = {
            "max_tokens": self.max_tokens,
            "temperature": self.temperature,
            "top_p": self.top_p,
            "streaming": self.streaming,
            "api_key": self.api_key,
            "base_url": self.base_url,
            "organization": self.organization,
            "model": self.get_model_name(),
            "model_kwargs": model_kwargs,
            "default_headers": {
                "HTTP-Referer": "https://github.com/lfnovo/esperanto",  # Required by OpenRouter
                "X-Title": "Esperanto",  # Required by OpenRouter
            },
        }

        # Ensure model name is set
        model_name = self.get_model_name()
        if not model_name:
            raise ValueError("Model name is required for Langchain integration.")
        langchain_kwargs["model"] = model_name  # Update model name in kwargs

        return ChatOpenAI(**self._clean_config(langchain_kwargs))

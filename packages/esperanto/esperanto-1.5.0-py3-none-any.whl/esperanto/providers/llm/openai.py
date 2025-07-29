"""OpenAI language model provider."""

import os
from typing import (
    TYPE_CHECKING,
    Any,
    AsyncGenerator,
    Dict,
    Generator,
    List,
    Optional,
    Union,
)

from openai import AsyncOpenAI, OpenAI
from openai.types.chat import ChatCompletion as OpenAIChatCompletion
from openai.types.chat import ChatCompletionChunk as OpenAIChatCompletionChunk

from esperanto.common_types import (
    ChatCompletion,
    ChatCompletionChunk,
    Choice,
    DeltaMessage,
    Message,
    Model,
    StreamChoice,
    Usage,
)
from esperanto.providers.llm.base import LanguageModel

if TYPE_CHECKING:
    from langchain_openai import ChatOpenAI


class OpenAILanguageModel(LanguageModel):
    """OpenAI language model implementation."""

    def __post_init__(self):
        """Initialize OpenAI client."""
        # Call parent's post_init to handle config initialization
        super().__post_init__()

        # Get API key
        self.api_key = self.api_key or os.getenv("OPENAI_API_KEY")
        if not self.api_key:
            raise ValueError("OpenAI API key not found")

        # Initialize clients
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

    @property
    def models(self) -> List[Model]:
        """List all available models for this provider."""
        models = self.client.models.list()
        return [
            Model(
                id=model.id,
                owned_by=model.owned_by,
                context_window=getattr(model, "context_window", None),
                type="language",
            )
            for model in models
            if model.id.startswith(
                ("gpt-")
            )  # Only include GPT models for language tasks
        ]

    def _normalize_response(self, response: OpenAIChatCompletion) -> ChatCompletion:
        """Normalize OpenAI response to our format."""
        return ChatCompletion(
            id=response.id,
            choices=[
                Choice(
                    index=choice.index,
                    message=Message(
                        content=choice.message.content or "",
                        role=choice.message.role,
                    ),
                    finish_reason=choice.finish_reason,
                )
                for choice in response.choices
            ],
            created=response.created,
            model=response.model,
            provider=self.provider,
            usage=Usage(
                completion_tokens=(
                    response.usage.completion_tokens if response.usage else 0
                ),
                prompt_tokens=response.usage.prompt_tokens if response.usage else 0,
                total_tokens=response.usage.total_tokens if response.usage else 0,
            ),
        )

    def _normalize_chunk(self, chunk: OpenAIChatCompletionChunk) -> ChatCompletionChunk:
        """Normalize OpenAI stream chunk to our format."""
        return ChatCompletionChunk(
            id=chunk.id,
            choices=[
                StreamChoice(
                    index=choice.index,
                    delta=DeltaMessage(
                        content=choice.delta.content or "",
                        role=choice.delta.role or "assistant",
                        function_call=(
                            dict(choice.delta.function_call)
                            if choice.delta.function_call
                            else None
                        ),
                        tool_calls=(
                            [
                                dict(tool_call.model_dump())  # Explicitly cast to dict
                                for tool_call in choice.delta.tool_calls
                            ]
                            if choice.delta.tool_calls
                            else None
                        ),
                    ),
                    finish_reason=choice.finish_reason,
                )
                for choice in chunk.choices
            ],
            created=chunk.created,
            model=chunk.model,
        )

    def _transform_messages_for_o1(
        self, messages: List[Dict[str, str]]
    ) -> List[Dict[str, str]]:
        """Transform messages for o1 models by replacing system role with user role."""
        return [
            {**msg, "role": "user"} if msg["role"] == "system" else {**msg}
            for msg in messages
        ]

    def _get_api_kwargs(self, exclude_stream: bool = False) -> Dict[str, Any]:
        """Get kwargs for API calls, filtering out provider-specific args.

        Args:
            exclude_stream: If True, excludes streaming-related parameters.
        """
        kwargs = {}
        config = self.get_completion_kwargs()
        model_name = self.get_model_name()
        is_reasoning_model = model_name.startswith("o1") or model_name.startswith("o3")

        # Only include non-provider-specific args that were explicitly set
        for key, value in config.items():
            if key not in [
                "model_name",
                "api_key",
                "base_url",
                "organization",
                "structured",
            ]:
                # Skip max_tokens if it's the default value (850) and we're using an o1 model
                if key == "max_tokens" and value == 850 and is_reasoning_model:
                    continue
                kwargs[key] = value

        # Special handling for o1 models
        if is_reasoning_model:
            # Replace max_tokens with max_completion_tokens
            if "max_tokens" in kwargs:
                kwargs["max_completion_tokens"] = kwargs.pop("max_tokens")
            kwargs.pop("temperature", None)
            kwargs.pop("top_p", None)

        # Handle streaming parameter
        if exclude_stream:
            kwargs.pop("streaming", None)
        elif "streaming" in kwargs:
            kwargs["stream"] = kwargs.pop("streaming")

        # Handle structured output
        if self.structured:
            if not isinstance(self.structured, dict):
                raise TypeError("structured parameter must be a dictionary")
            structured_type = self.structured.get("type")
            if structured_type in ["json", "json_object"]:
                kwargs["response_format"] = {"type": "json_object"}

        return kwargs

    def chat_complete(
        self, messages: List[Dict[str, str]], stream: Optional[bool] = None
    ) -> Union[ChatCompletion, Generator[ChatCompletionChunk, None, None]]:
        """Send a chat completion request.

        Args:
            messages: List of messages in the conversation.
            stream: Whether to stream the response. If None, uses the instance's streaming setting.

        Returns:
            Either a ChatCompletion or a Generator yielding ChatCompletionChunks if streaming.
        """
        should_stream = stream if stream is not None else self.streaming
        model_name = self.get_model_name()
        is_reasoning_model = model_name.startswith("o1") or model_name.startswith("o3")
        # Transform messages for o1 models
        if is_reasoning_model:
            messages = self._transform_messages_for_o1(
                [{**msg} for msg in messages]
            )  # Deep copy each message dict

        response = self.client.chat.completions.create(
            messages=messages,
            model=model_name,
            stream=should_stream,
            **self._get_api_kwargs(exclude_stream=True),
        )

        if should_stream:
            return (self._normalize_chunk(chunk) for chunk in response)
        return self._normalize_response(response)

    async def achat_complete(
        self, messages: List[Dict[str, str]], stream: Optional[bool] = None
    ) -> Union[ChatCompletion, AsyncGenerator[ChatCompletionChunk, None]]:
        """Send an async chat completion request.

        Args:
            messages: List of messages in the conversation.
            stream: Whether to stream the response. If None, uses the instance's streaming setting.

        Returns:
            Either a ChatCompletion or an AsyncGenerator yielding ChatCompletionChunks if streaming.
        """
        should_stream = stream if stream is not None else self.streaming
        model_name = self.get_model_name()
        is_reasoning_model = model_name.startswith("o1") or model_name.startswith("o3")
        # Transform messages for o1 models
        if is_reasoning_model:
            messages = self._transform_messages_for_o1(
                [{**msg} for msg in messages]
            )  # Deep copy each message dict

        response = await self.async_client.chat.completions.create(
            messages=messages,
            model=model_name,
            stream=should_stream,
            **self._get_api_kwargs(exclude_stream=True),
        )

        if should_stream:

            async def generate():
                async for chunk in response:
                    yield self._normalize_chunk(chunk)

            return generate()
        return self._normalize_response(response)

    def _get_default_model(self) -> str:
        """Get the default model name."""
        return "gpt-4"

    @property
    def provider(self) -> str:
        """Get the provider name."""
        return "openai"

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
                "Install with: uv add esperanto[openai,langchain] or pip install esperanto[openai,langchain]"
            ) from e

        model_kwargs = {}
        if self.structured == "json":
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
        }

        is_reasoning_model = self.get_model_name().startswith(
            "o1"
        ) or self.get_model_name().startswith("o3")

        if is_reasoning_model:
            # Replace max_tokens with max_completion_tokens
            if "max_tokens" in langchain_kwargs:
                langchain_kwargs["max_completion_tokens"] = langchain_kwargs.pop(
                    "max_tokens"
                )
            langchain_kwargs["temperature"] = 1
            langchain_kwargs["top_p"] = None

        return ChatOpenAI(**self._clean_config(langchain_kwargs))

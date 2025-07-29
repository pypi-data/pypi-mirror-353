from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from esperanto.providers.llm.google import GoogleLanguageModel
from esperanto.providers.llm.groq import GroqLanguageModel
from esperanto.providers.llm.openai import OpenAILanguageModel


@pytest.fixture
def mock_openai_response():
    mock_response = MagicMock()
    mock_response.id = "chatcmpl-123"
    mock_response.created = 1677858242
    mock_response.model = "gpt-4"

    mock_message = MagicMock()
    mock_message.content = "Test response"
    mock_message.role = "assistant"

    mock_choice = MagicMock()
    mock_choice.index = 0
    mock_choice.message = mock_message
    mock_choice.finish_reason = "stop"

    mock_response.choices = [mock_choice]

    mock_usage = MagicMock()
    mock_usage.completion_tokens = 10
    mock_usage.prompt_tokens = 20
    mock_usage.total_tokens = 30
    mock_response.usage = mock_usage

    return mock_response


@pytest.fixture
def openai_model():
    with (
        patch("openai.OpenAI") as mock_openai,
        patch("openai.AsyncOpenAI") as mock_async_openai,
    ):

        # Create mock response
        mock_response = MagicMock()
        mock_response.id = "chatcmpl-123"
        mock_response.created = 1677858242
        mock_response.model = "gpt-4"
        mock_response.object = "chat.completion"

        mock_message = MagicMock()
        mock_message.content = "Test response"
        mock_message.role = "assistant"
        mock_message.function_call = None
        mock_message.tool_calls = None

        mock_choice = MagicMock()
        mock_choice.index = 0
        mock_choice.message = mock_message
        mock_choice.finish_reason = "stop"
        mock_choice.logprobs = None

        mock_response.choices = [mock_choice]

        mock_usage = MagicMock()
        mock_usage.completion_tokens = 10
        mock_usage.prompt_tokens = 20
        mock_usage.total_tokens = 30
        mock_response.usage = mock_usage

        # Mock the sync client
        mock_chat = MagicMock()
        mock_chat.completions = MagicMock()
        mock_chat.completions.create = MagicMock(return_value=mock_response)

        mock_sync_instance = MagicMock()
        mock_sync_instance.chat = mock_chat
        mock_openai.return_value = mock_sync_instance

        # Mock the async client
        mock_async_chat = MagicMock()
        mock_async_chat.completions = MagicMock()
        mock_async_chat.completions.create = AsyncMock(return_value=mock_response)

        mock_async_instance = MagicMock()
        mock_async_instance.chat = mock_async_chat
        mock_async_openai.return_value = mock_async_instance

        # Create the model with a test API key
        model = OpenAILanguageModel(api_key="test-key")

        # Replace the actual clients with our mocked ones
        model.client = mock_sync_instance
        model.async_client = mock_async_instance

        yield model


@pytest.fixture
def google_model():
    with patch("google.genai.Client") as mock_client:
        # Create mock client instance
        mock_client_instance = MagicMock()
        mock_client.return_value = mock_client_instance

        # Mock the models object (sync)
        mock_models = MagicMock()
        mock_client_instance.models = mock_models
        # Mock the aio.models object (async)
        mock_aio = MagicMock()
        mock_client_instance.aio = MagicMock()
        mock_client_instance.aio.models = mock_aio

        # Mock generate_content method for sync
        mock_part = MagicMock()
        mock_part.text = "Hello! How can I help you today?"
        mock_part.strip = lambda: "Hello! How can I help you today?"

        mock_content = MagicMock()
        mock_content.parts = [mock_part]

        mock_candidate = MagicMock()
        mock_candidate.content = mock_content
        mock_candidate.finish_reason = "STOP"

        mock_response = MagicMock()
        mock_response.candidates = [mock_candidate]
        mock_response.prompt_feedback = MagicMock()
        mock_response.prompt_feedback.block_reason = None

        # Async response
        mock_async_response = MagicMock()
        mock_async_response.candidates = [mock_candidate]

        # Streaming async generator
        async def async_stream_response(*args, **kwargs):
            yield mock_response

        # Assign the mocks
        mock_models.generate_content = MagicMock(return_value=mock_response)
        mock_models.generate_content_async = AsyncMock(return_value=mock_async_response)
        mock_models.list_models = MagicMock(return_value=[])
        # Patch aio.models for new SDK async usage
        mock_aio.generate_content = AsyncMock(return_value=mock_async_response)
        mock_aio.generate_content_stream = AsyncMock(return_value=async_stream_response())

        # Initialize model with test key
        model = GoogleLanguageModel(api_key="test-key")
        model._client = mock_client_instance

        yield model


@pytest.fixture
def mock_groq_response():
    mock_response = MagicMock()
    mock_response.id = "chatcmpl-123"
    mock_response.created = 1677858242
    mock_response.model = "mixtral-8x7b-32768"

    mock_message = MagicMock()
    mock_message.content = "Test response"
    mock_message.role = "assistant"

    mock_choice = MagicMock()
    mock_choice.index = 0
    mock_choice.message = mock_message
    mock_choice.finish_reason = "stop"

    mock_response.choices = [mock_choice]

    mock_usage = MagicMock()
    mock_usage.completion_tokens = 10
    mock_usage.prompt_tokens = 20
    mock_usage.total_tokens = 30
    mock_response.usage = mock_usage

    return mock_response


@pytest.fixture
def groq_model():
    with patch("groq.Groq") as mock_groq, patch("groq.AsyncGroq") as mock_async_groq:

        # Create mock response
        mock_response = MagicMock()
        mock_response.id = "chatcmpl-123"
        mock_response.created = 1677858242
        mock_response.model = "mixtral-8x7b-32768"
        mock_response.object = "chat.completion"

        mock_message = MagicMock()
        mock_message.content = "Test response"
        mock_message.role = "assistant"
        mock_message.function_call = None
        mock_message.tool_calls = None

        mock_choice = MagicMock()
        mock_choice.index = 0
        mock_choice.message = mock_message
        mock_choice.finish_reason = "stop"
        mock_choice.logprobs = None

        mock_response.choices = [mock_choice]

        mock_usage = MagicMock()
        mock_usage.completion_tokens = 10
        mock_usage.prompt_tokens = 8
        mock_usage.total_tokens = 18
        mock_response.usage = mock_usage

        # Mock the sync client
        mock_chat = MagicMock()
        mock_chat.completions = MagicMock()
        mock_chat.completions.create = MagicMock(return_value=mock_response)

        mock_sync_instance = MagicMock()
        mock_sync_instance.chat = mock_chat
        mock_groq.return_value = mock_sync_instance

        # Mock the async client
        mock_async_chat = MagicMock()
        mock_async_chat.completions = MagicMock()
        mock_async_chat.completions.create = AsyncMock(return_value=mock_response)

        mock_async_instance = MagicMock()
        mock_async_instance.chat = mock_async_chat
        mock_async_groq.return_value = mock_async_instance

        # Create the model with a test API key
        model = GroqLanguageModel(api_key="test-key")

        # Replace the actual clients with our mocked ones
        model.client = mock_sync_instance
        model.async_client = mock_async_instance

        yield model

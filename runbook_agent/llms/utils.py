import datetime
from pydantic import BaseModel
from typing import List, Optional
from enum import Enum
from runbook_agent.config import init_config

cfg = init_config()


class AnthropicContent(BaseModel):
    text: str
    type: str


class AnthropicUsage(BaseModel):
    input_tokens: int
    output_tokens: int
    total_tokens: Optional[int] = None


class AnthropicResponse(BaseModel):
    id: str
    content: List[AnthropicContent]
    model: str
    role: str
    stop_reason: Optional[str] = None
    usage: AnthropicUsage


class OpenAIMessage(BaseModel):
    role: str
    content: str


class OpenAIChoice(BaseModel):
    index: int
    message: OpenAIMessage
    finish_reason: Optional[str] = None


class OpenAIUsage(BaseModel):
    prompt_tokens: int
    completion_tokens: int
    total_tokens: int


class OpenAIResponse(BaseModel):
    id: str
    object: str
    created: int
    choices: List[OpenAIChoice]
    usage: OpenAIUsage


class Providers(Enum):
    OPENAI = "openai"
    ANTHROPIC = "anthropic"


def convert_anthropic_to_openai_response_format(
    anthropic_response: AnthropicResponse,
) -> OpenAIResponse:
    """
    Converts an AnthropicResponse Pydantic model to an OpenAIResponse Pydantic model.

    Args:
        anthropic_response (AnthropicResponse): The response from Anthropic API.

    Returns:
        OpenAIResponse: The response in OpenAI ChatCompletion format.
    """
    anthropic_response = AnthropicResponse(**anthropic_response.model_dump())
    # Concatenate all text blocks from Anthropic response content
    combined_content = " ".join(content.text for content in anthropic_response.content)

    # Calculate total tokens if not provided
    total_tokens = anthropic_response.usage.total_tokens or (
        anthropic_response.usage.input_tokens + anthropic_response.usage.output_tokens
    )

    # Create OpenAIUsage instance
    openai_usage = OpenAIUsage(
        prompt_tokens=anthropic_response.usage.input_tokens,
        completion_tokens=anthropic_response.usage.output_tokens,
        total_tokens=total_tokens,
    )

    # Create OpenAIMessage instance
    openai_message = OpenAIMessage(
        role=anthropic_response.role, content=combined_content
    )

    # Create OpenAIChoice instance
    openai_choice = OpenAIChoice(
        index=0, message=openai_message, finish_reason=anthropic_response.stop_reason
    )

    # Create OpenAIResponse instance
    openai_response = OpenAIResponse(
        id=anthropic_response.id,
        object="chat.completion",
        created=int(datetime.datetime.now().timestamp()),
        choices=[openai_choice],
        usage=openai_usage,
    )

    return openai_response


def get_default_model_for_provider(provider: Providers):
    """
    Returns the default model for the given provider.
    Args:
        provider (Optional[Providers]): The provider to get the default model for.
    Returns:
        str: The default model for the given provider.
    """
    if provider == Providers.OPENAI.value:
        # if provider is OpenAI , return the default model for the OpenAI provider
        return cfg.openai.GPT_4O_MINI
    elif provider == Providers.ANTHROPIC.value:
        # if provider is Anthropic , return the default model for the Anthropic provider
        return cfg.anthropic.CLAUDE_3_5_SONNET
    else:
        # raise ValueError if the provider is not supported
        raise ValueError(f"Invalid provider: {provider}")

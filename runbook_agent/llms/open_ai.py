import logging
from tenacity import retry, wait_random_exponential, stop_after_attempt
from typing import Optional
from runbook_agent.llms.llm_clients import (
    openai_client,
    async_openai_client,
    openai_instructor,
    openai_instructor_async,
    anthropic_client,
    anthropic_async_client,
    anthropic_instructor,
    anthropic_instructor_async,
)
from runbook_agent import config
from runbook_agent.llms.utils import (
    Providers,
    convert_anthropic_to_openai_response_format,
    get_default_model_for_provider,
)

# Initialize config
cfg = config.init_config()

# logging
log = logging.getLogger(__name__)


@retry(wait=wait_random_exponential(min=1, max=40), stop=stop_after_attempt(5))
def chat_completion_request(
    messages,
    temperature=0,
    seed=123,
    model=None,
    top_p=1,
    response_format={"type": "text"},
    max_tokens=None,
    tools=None,
    function_call=None,
    provider: Optional[str] = None,
    tool_choice=None,
):
    # if provider is None , assign default provider as OpenAI
    provider = provider or Providers.OPENAI.value
    # provider is OpenAI
    if provider == Providers.OPENAI.value:
        model = model or get_default_model_for_provider(provider)
        try:
            completion = openai_client.chat.completions.create(
                model=model,
                messages=messages,
                temperature=temperature,
                seed=seed,
                top_p=top_p,
                response_format=response_format,
                max_tokens=max_tokens,
                tools=tools,
                function_call=function_call,
                tool_choice=tool_choice,
            )

            # Extract token usage from the completion response
            total_tokens = completion.usage.total_tokens
            input_tokens = completion.usage.prompt_tokens
            output_tokens = completion.usage.completion_tokens
            return completion, (total_tokens, input_tokens, output_tokens)
        except Exception as e:
            logging.exception("Unable to generate ChatCompletion response")
            logging.error(f"Exception: {e}")
            return None, (0, 0, 0)
    # provider is Anthropic
    elif provider == Providers.ANTHROPIC.value:
        model = model or get_default_model_for_provider(provider)
        try:
            completion = anthropic_client.messages.create(
                messages=messages,
                model=model,
                tools=tools,
                max_tokens=max_tokens,
                tool_choice=tool_choice,
            )
            completion = convert_anthropic_to_openai_response_format(completion)
            # Extract token usage from the completion response
            total_tokens = completion.usage.total_tokens
            input_tokens = completion.usage.prompt_tokens
            output_tokens = completion.usage.completion_tokens
            return completion, (total_tokens, input_tokens, output_tokens)
        except Exception as e:
            logging.exception("Unable to generate ChatCompletion response")
            logging.error(f"Exception: {e}")
            return None, (0, 0, 0)
    else:
        raise ValueError(f"Invalid provider: {provider}")


@retry(wait=wait_random_exponential(min=1, max=40), stop=stop_after_attempt(5))
def chat_completion_request_instructor(
    messages,
    temperature=0,
    seed=123,
    model=None,
    top_p=1,
    max_tokens=None,
    tools=None,
    function_call=None,
    response_model=None,
    provider: Optional[str] = None,
):
    # if provider is None , assign default provider as OpenAI
    provider = provider or Providers.OPENAI.value

    if provider == Providers.OPENAI.value:
        model = model or get_default_model_for_provider(provider)

        try:
            completion = openai_instructor.chat.completions.create(
                model=model,
                messages=messages,
                temperature=temperature,
                seed=seed,
                top_p=top_p,
                max_tokens=max_tokens,
                tools=tools,
                function_call=function_call,
                response_model=response_model,
            )
            return completion
        except Exception as e:
            logging.exception("Unable to generate ChatCompletion response")
            logging.error(f"Exception: {e}")
            return None
    elif provider == Providers.ANTHROPIC.value:
        model = model or get_default_model_for_provider(provider)
        try:
            completion = anthropic_instructor.chat.completions.create(
                model=model,
                messages=messages,
                max_tokens=max_tokens,
                response_model=response_model,
            )
            return completion
        except Exception as e:
            logging.exception("Unable to generate ChatCompletion response")
            logging.error(f"Exception: {e}")
            return None
    else:
        raise ValueError(f"Invalid provider: {provider}")


@retry(wait=wait_random_exponential(min=1, max=40), stop=stop_after_attempt(5))
async def async_chat_completion_request_instructor(
    messages,
    temperature=0,
    seed=123,
    model=None,
    top_p=1,
    max_tokens=None,
    tools=None,
    function_call=None,
    response_model=None,
    provider: Optional[str] = None,
):
    # if provider is None , assign default provider as OpenAI
    provider = provider or Providers.OPENAI.value

    if provider == Providers.OPENAI.value:
        model = model or get_default_model_for_provider(provider)

        try:
            return await openai_instructor_async.chat.completions.create(
                model=model,
                messages=messages,
                temperature=temperature,
                seed=seed,
                top_p=top_p,
                max_tokens=max_tokens,
                tools=tools,
                function_call=function_call,
                response_model=response_model,
            )

            # # Extract token usage from the completion response
            # total_tokens = completion.usage.total_tokens
            # input_tokens = completion.usage.prompt_tokens
            # output_tokens = completion.usage.completion_tokens
            # return completion, (total_tokens, input_tokens, output_tokens)
            # return completion
        except Exception as e:
            logging.exception("Unable to generate ChatCompletion response")
            logging.error(f"Exception: {e}")
            return None
    elif provider == Providers.ANTHROPIC.value:
        model = model or get_default_model_for_provider(provider)

        try:
            return await anthropic_instructor_async.chat.completions.create(
                model=model,
                messages=messages,
                max_tokens=max_tokens,
                response_model=response_model,
            )
        except Exception as e:
            logging.exception("Unable to generate ChatCompletion response")
            logging.error(f"Exception: {e}")
            return None
    else:
        raise ValueError(f"Invalid provider: {provider}")


@retry(wait=wait_random_exponential(min=1, max=40), stop=stop_after_attempt(5))
async def async_chat_completion_request(
    messages,
    temperature=0,
    seed=123,
    model=None,
    top_p=1,
    response_format={"type": "text"},
    max_tokens=None,
    functions=None,
    function_call=None,
    provider: Optional[str] = None,
):
    # if provider is None , assign default provider as OpenAI
    provider = provider or Providers.OPENAI.value

    if provider == Providers.OPENAI.value:
        model = model or get_default_model_for_provider(provider)

        try:
            completion = await async_openai_client.chat.completions.create(
                model=model,
                messages=messages,
                temperature=temperature,
                seed=seed,
                top_p=top_p,
                response_format=response_format,
                max_tokens=max_tokens,
                functions=functions,
                function_call=function_call,
            )

            # Extract token usage from the completion response
            total_tokens = completion.usage.total_tokens
            input_tokens = completion.usage.prompt_tokens
            output_tokens = completion.usage.completion_tokens
            return completion, (total_tokens, input_tokens, output_tokens)
        except Exception as e:
            logging.exception("Unable to generate ChatCompletion response")
            logging.error(f"Exception: {e}")
            return None, (0, 0, 0)
    elif provider == Providers.ANTHROPIC.value:
        model = model or get_default_model_for_provider(provider)

        try:
            completion = await anthropic_async_client.messages.create(
                messages=messages,
                model=model,
                max_tokens=max_tokens,
            )
            completion = convert_anthropic_to_openai_response_format(completion)
            # Extract token usage from the completion response
            total_tokens = completion.usage.total_tokens
            input_tokens = completion.usage.prompt_tokens
            output_tokens = completion.usage.completion_tokens
            return completion, (total_tokens, input_tokens, output_tokens)
        except Exception as e:
            logging.exception("Unable to generate ChatCompletion response")
            logging.error(f"Exception: {e}")
            return None
    else:
        raise ValueError(f"Invalid provider: {provider}")


def vision_completion_request(image_url, model=None):
    if model is None:
        model = cfg.openai.VISION_MODEL

    messages = [
        {
            "role": "user",
            "content": [
                {
                    "type": "text",
                    "text": "What’s in this image? Extract all the number, names, dates, etc.",
                },
                {"type": "image_url", "image_url": {"url": image_url}},
            ],
        }
    ]

    try:
        response = openai_client.chat.completions.create(
            model=model, messages=messages, temperature=0.2, max_tokens=500
        )
        return response
    except Exception as e:
        return str(e)


@retry(wait=wait_random_exponential(min=1, max=40), stop=stop_after_attempt(5))
def embeddings_request(text, model=None, dimensions=None):
    """
    Generate embeddings for the given text using the specified model.

    :param text: The text for which to generate embeddings.
    :param model: The model to use for generating embeddings. Default is "text-embedding-ada-002".
    :return: The embeddings as a list of floats.
    """
    if model is None:
        model = cfg.openai.EMBEDDING_MODEL
    if dimensions is None:
        dimensions = cfg.rag.DIMENSIONS

    try:
        response = openai_client.embeddings.create(
            model=model, input=text, encoding_format="float", dimensions=dimensions
        )
        return response
    except Exception as e:
        logging.error("Unable to generate embeddings")
        logging.error(f"Exception: {e}")
        raise e

import openai
import logging
import requests
from tenacity import retry, wait_random_exponential, stop_after_attempt
from runbook_agent import config

# Initialize config
cfg = config.init_config()

# Set Azure OpenAI API details
openai.api_key = cfg.azure_openai_api.API_KEY
openai.api_base = cfg.azure_openai_api.URL
openai.api_type = cfg.azure_openai_api.API_TYPE
openai.api_version = cfg.azure_openai_api.API_VERSION

# Configure logging
logging.basicConfig(
    level=cfg.LOGGING_LEVEL,
    format="%(asctime)s [%(filename)s:%(funcName)s:%(lineno)d] %(levelname)s - %(message)s",
)


@retry(wait=wait_random_exponential(min=1, max=40), stop=stop_after_attempt(3))
def azure_chat_completion_request(messages, model=None):
    if model is None:
        model = cfg.azure_openai_api.CONVERSATION_MODEL

    api_url = f"{cfg.azure_openai_api.URL}/openai/deployments/{model}/chat/completions?api-version={cfg.azure_openai_api.API_VERSION}"
    json_data = {"model": model, "messages": messages, "temperature": 0}

    try:
        response = requests.post(
            api_url,
            headers=cfg.azure_openai_api.HEADERS,
            json=json_data,
        )
        return response
    except Exception as e:
        logging.error("Unable to generate Azure ChatCompletion response")
        logging.error(f"Exception: {e}")
        return str(e)


# Example usage
# print('Sending a test completion job')

# messages = [{"role":"system", "content":"you are an ecommerce chatbot"}]
# messages.append({"role":"user", "content":"hi"})

# response = azure_chat_completion_request(messages)
# print("response.status_code = ",response.status_code)
# response = response.json()
# print(response['choices'][0]['message']['content'])

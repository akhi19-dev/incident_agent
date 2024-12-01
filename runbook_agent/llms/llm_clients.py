from runbook_agent.config import init_config
import instructor
from openai import OpenAI, AsyncOpenAI
from anthropic import AnthropicBedrock, AsyncAnthropicBedrock


# Config
cfg = init_config()
# openai
openai_client = OpenAI(api_key=cfg.openai.API_KEY)
async_openai_client = AsyncOpenAI(api_key=cfg.openai.API_KEY)
openai_instructor = instructor.from_openai(openai_client)
openai_instructor_async = instructor.from_openai(async_openai_client)
# Anthropic
anthropic_client = AnthropicBedrock(
    aws_access_key=cfg.aws.access_key_id,
    aws_secret_key=cfg.aws.secret_access_key,
    aws_region=cfg.aws.region,
)
anthropic_async_client = AsyncAnthropicBedrock(
    aws_access_key=cfg.aws.access_key_id,
    aws_secret_key=cfg.aws.secret_access_key,
    aws_region=cfg.aws.region,
)
anthropic_instructor = instructor.from_anthropic(anthropic_client)
anthropic_instructor_async = instructor.from_anthropic(anthropic_async_client)

# Import required modules
from dotenv import load_dotenv
from easydict import EasyDict as edict
from typing import Any
import os

# Load environment variables from the .env file
load_dotenv()


def init_config() -> edict[Any]:
    cfg = edict()
    cfg.openai = edict()
    cfg.openai.API_KEY = os.getenv("OPENAI_API_KEY")
    # AWS
    cfg.aws = edict()
    cfg.aws.access_key_id = os.getenv("AWS_ACCESS_KEY_ID")
    cfg.aws.secret_access_key = os.getenv("AWS_SECRET_ACCESS_KEY")
    cfg.aws.region = os.getenv("AWS_REGION")
    # LanceDB
    cfg.lance = edict()
    cfg.lance.db_uri = os.getenv("LANCE_DB_URI")
    return cfg

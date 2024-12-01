from runbook_agent.logger import get_logger

log = get_logger(__name__)


class TokenManager:
    """
    TokenManager is a class that is used to manage the token counts for the models.
    """

    _instance = None

    @classmethod
    def get_instance(cls):
        """
        Get the instance of the class.
        """
        # lazy init
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance

    def __init__(self):
        """
        Initialize the class.
        """
        self.token_count = {
            "total_token": 0,
            "total_input_token": 0,
            "total_output_token": 0,
            "token_per_model": {
                "gpt-4": {"input": 0.0, "output": 0.0},
                "gpt-4-0125-preview": {"input": 0.0, "output": 0.0},
                "gpt-4-1106-preview": {"input": 0.0, "output": 0.0},
                "gpt-4-1106-vision-preview": {"input": 0.0, "output": 0.0},
                "gpt-4-turbo-2024-04-09": {"input": 0.0, "output": 0.0},
                "gpt-4o-2024-05-13": {"input": 0.0, "output": 0.0},
                "gpt-3.5-turbo-0613": {"input": 0.0, "output": 0.0},
                "gpt-3.5-turbo-0125": {"input": 0.0, "output": 0.0},
                "gpt-3.5-turbo-instruct": {"input": 0.0, "output": 0.0},
            },
        }

    def update_tokens(self, tokens, model_type):
        """
        Update the token counts for the model.
        Args:
            tokens (tuple): A tuple of the total tokens, input tokens, and output tokens.
            model_type (str): The type of the model.
        """
        total_tokens, input_tokens, output_tokens = tokens
        self.token_count["total_token"] += total_tokens
        self.token_count["total_input_token"] += input_tokens
        self.token_count["total_output_token"] += output_tokens

        if model_type not in self.token_count["token_per_model"]:
            self.token_count["token_per_model"][model_type] = {
                "input": 0.0,
                "output": 0.0,
            }

        self.token_count["token_per_model"][model_type]["input"] += input_tokens
        self.token_count["token_per_model"][model_type]["output"] += output_tokens

        log.debug(f"Updated token counts for model {model_type}: {self.token_count}")

    def print_token_counts(self):
        """
        Print the token counts for the models.
        """
        for model_type, counts in self.token_count["token_per_model"].items():
            log.debug(
                f"Model {model_type}: Input Tokens: {counts['input']}, Output Tokens: {counts['output']}"
            )
        log.debug(
            f"Total Tokens: {self.token_count['total_token']}, Total Input Tokens: {self.token_count['total_input_token']}, Total Output Tokens: {self.token_count['total_output_token']}"
        )


class TokenCountingMixin:
    """
    TokenCountingMixin is a class that is used to mixin the token counting functionality to the models.
    """

    def update_tokens(self, tokens, model_type):
        """
        Update the token counts for the model.
        """
        token_manager = TokenManager.get_instance()
        token_manager.update_tokens(tokens, model_type)

from core.llm.groq_client import Groq
from core.llm.openai_client import OpenAi
from core.llm.claude_client import Claude
from typing import List, Tuple

from typing import List, Tuple

class LLM:
    models = {
        "CLAUDE": [
            ("Claude 3 Opus", "claude-3-opus-20240229"),
            ("Claude 3 Sonnet", "claude-3-sonnet-20240229"),
            ("Claude 3 Haiku", "claude-3-haiku-20240307"),
        ],
        "OPENAI": [
            ("GPT-4o", "gpt-4o"),
            ("GPT-4 Turbo", "gpt-4-turbo"),
            ("GPT-3.5 Turbo", "gpt-3.5-turbo-0125"),
        ],
        "GOOGLE": [
            ("Gemini 1.0 Pro", "gemini-pro"),
            ("Gemini 1.5 Flash", "gemini-1.5-flash"),
            ("Gemini 1.5 Pro", "gemini-1.5-pro"),
        ],
        "MISTRAL": [
            ("Mistral 7b", "open-mistral-7b"),
            ("Mistral 8x7b", "open-mixtral-8x7b"),
            ("Mistral Medium", "mistral-medium-latest"),
            ("Mistral Small", "mistral-small-latest"),
            ("Mistral Large", "mistral-large-latest"),
        ],
        "GROQ": [
            ("LLAMA3 8B", "llama3-8b-8192"),
            ("LLAMA3 70B", "llama3-70b-8192"),
            ("LLAMA2 70B", "llama2-70b-4096"),
            ("Mixtral", "mixtral-8x7b-32768"),
            ("GEMMA 7B", "gemma-7b-it"),
        ],
        "OLLAMA": []
    }

    def __init__(self, model_id: str = None):
        self.model_id = model_id

    @classmethod
    def list_models(cls) -> dict:
        return cls.models

    @classmethod
    def model_enum(cls, model_name: str) -> Tuple[str, str]:
        model_dict = {
            model[0]: (model_enum, model[1]) 
            for model_enum, models in cls.models.items() 
            for model in models
        }
        return model_dict.get(model_name, (None, None))

    @classmethod
    def check_model(cls, model_name: str):
        # Raise an error if the selected model is not available
        model_enum, model_id = cls.model_enum(model_name)
        if model_enum is None:
            available_models = [model[0] for models in cls.models.values() for model in models]
            raise ValueError(f"Unsupported model: {model_name}\n Available models: {available_models}")

    @staticmethod
    def inference_with_model(model_enum: str, model_id: str, prompt: str, response_model: str = None) -> any:
        if model_enum == "GROQ":
            from core.llm.groq_client import Groq
            return Groq().inference(model_id, prompt, response_model)
        elif model_enum == "OPENAI":
            from core.llm.openai_client import OpenAi
            return OpenAi().inference(model_id, prompt, response_model)
        elif model_enum == "CLAUDE":
            from core.llm.claude_client import Claude
            return Claude().inference(model_id, prompt, response_model)
        else:
            raise ValueError(f"Unsupported model: {model_id}")

    def inference(self, prompt: str, response_model: str = None) -> any:
        model_enum, model_id = self.model_enum(self.model_id)
        return self.inference_with_model(model_enum, model_id, prompt, response_model)
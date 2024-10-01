from core.llm.groq_client import Groq
from core.llm.openai_client import OpenAi
from core.llm.claude_client import Claude
from typing import List, Tuple

class LLM:
    def __init__(self, language: str):
        self.language = language
        self.models = {
            "OPENAI": {
                "en": "gpt-4o",  # Default OpenAI model for English
                "hi": "gpt-4o",  # Default OpenAI model for Hindi
            },
            "CLAUDE": {
                "en": "claude-3-opus-20240229",  # Default Claude model for English
                "hi": "claude-3-opus-20240229",  # Default Claude model for Hindi
            },
            "GOOGLE": {
                "en": "gemini-pro",  # Default Google model for English
                "hi": "gemini-pro",  # Default Google model for Hindi
            },
            "GROQ": {
                "en": "llama3-8b-8192",  # Default GROQ model for English
                "hi": None,  # No Hindi support in GROQ models for now
            },
            "MISTRAL": {
                "en": "open-mistral-7b",  # Default Mistral model for English
                "hi": None,  # No Hindi support in Mistral models
            },
            "OLLAMA": {
                "en": None,  # No default models yet
                "hi": None,
            },
        }
        self.model_id, self.model_enum = self._select_model()

    def _select_model(self) -> Tuple[str, str]:
        for model_enum, lang_models in self.models.items():
            if self.language in lang_models and lang_models[self.language]:
                return lang_models[self.language], model_enum
        raise ValueError(f"Unsupported language: {self.language} or no models available for this language")

    def list_models(self):
        return self.models

    def inference(self, prompt: str, response_model: str = None) -> any:
        if self.model_enum == "GROQ":
            return Groq().inference(self.model_id, prompt, response_model)
        elif self.model_enum == "OPENAI":
            return OpenAi().inference(self.model_id, prompt, response_model)
        elif self.model_enum == "CLAUDE":
            return Claude().inference(self.model_id, prompt, response_model)
        else:
            return "Model not found"
from core.llm.groq_client import Groq
from core.llm.openai_client import OpenAi
from core.llm.claude_client import Claude
from typing import List, Tuple

class LLM:
    def __init__(self, model_id: str = None):
        self.model_id = model_id
        self.models = {
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

    def list_models(self):
        return self.models
    
    def model_enum(self, model_name: str) -> Tuple[str, str]:
        model_dict = {
            model[0]: (model_enum, model[1]) 
            for model_enum, models in self.models.items() 
            for model in models
        }
        return model_dict.get(model_name, (None, None))
    
    def inference(self, prompt: str, response_model: str = None) -> any:
        model_enum, model_id = self.model_enum(self.model_id)
        if model_enum == "GROQ":
            return Groq().inference(model_id, prompt, response_model)
        elif model_enum == "OPENAI":
            return OpenAi().inference(model_id, prompt, response_model)
        elif model_enum == "CLAUDE":
            return Claude().inference(model_id, prompt, response_model)
        else:
            return "Model not found"
        

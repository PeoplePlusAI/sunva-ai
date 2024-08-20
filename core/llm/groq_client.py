from groq import Groq as _Groq
from pydantic import BaseModel
from dotenv import load_dotenv
import instructor
import os

load_dotenv("ops/.env")

api_key = os.getenv("GROQ_API_KEY")


class Groq:
    def __init__(self):
        api_key = os.getenv("GROQ_API_KEY")
        self.client = _Groq(api_key=api_key)

    def inference(self, model_id: str, prompt: str, response_model: BaseModel) -> str:
        self.client = instructor.patch(self.client)
        chat_completion = self.client.chat.completions.create(
            response_model=response_model,
            messages=[
                {
                    "role": "system",
                    "content": prompt,
                }
            ],
            model=model_id,
        )
        return chat_completion
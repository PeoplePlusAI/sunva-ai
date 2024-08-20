from openai import OpenAI
from pydantic import BaseModel
from dotenv import load_dotenv
import instructor
import os

load_dotenv(
    "ops/.env"
)

class OpenAi:
    def __init__(self):
        self.api_key = os.getenv("OPENAI_API_KEY")
        self.client = instructor.patch(
            OpenAI(api_key=self.api_key)
        )

    def inference(self, model_id: str, prompt: str, response_model: BaseModel) -> str:
        chat_completion = self.client.chat.completions.create(
            response_model=response_model,
            messages=[
                {
                    "role": "user",
                    "content": prompt.strip(),
                }
            ],
            model=model_id,
        )
        return chat_completion
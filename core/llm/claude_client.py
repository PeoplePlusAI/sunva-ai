from anthropic import Anthropic
from pydantic import BaseModel, ValidationError
from dotenv import load_dotenv
import instructor
import os

load_dotenv("ops/.env")

class Claude:
    def __init__(self):
        api_key = os.getenv("CLAUDE_API_KEY")
        self.client = Anthropic(
            api_key=api_key,
        )

    def inference(self, model_id: str, prompt: str, response_model: BaseModel) -> str:
        self.client = instructor.from_anthropic(self.client)
        try:
            message = self.client.messages.create(
                max_tokens=4096,
                messages=[
                    {
                        "role": "user",
                        "content": prompt.strip(),
                    }
                ],
                model=model_id,
                response_model=response_model,
                temperature=0
            )
        except ValidationError as e:
            print(e)
        return message
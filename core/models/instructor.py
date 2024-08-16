from pydantic import BaseModel

class ProcessedText(BaseModel):
    processed_text: str


class ProcessingDecision(BaseModel):
    decision: bool
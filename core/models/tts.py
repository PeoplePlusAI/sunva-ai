from pydantic import BaseModel


# Pydantic model for WebSocket response
class TTSResponse(BaseModel):
    audio: str
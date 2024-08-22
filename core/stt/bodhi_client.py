import asyncio
import json
import os
import websockets
import io

class BodhiSTT:
    def __init__(self, model: str = "hi-general-v2-8khz", language: str = "hi"):
        self.model = model
        self.language = language
        self.server_addr = "wss://bodhi.navana.ai"
        self.api_key = os.environ.get("API_KEY")
        self.customer_id = os.environ.get("CUSTOMER_ID")

    async def transcribe_stream(self, audio_buffer: io.BytesIO, chunk_size: int = 4096):
        if not self.api_key or not self.customer_id:
            raise ValueError("Please set API key and customer ID in environment variables.")

        request_headers = {
            "x-api-key": self.api_key,
            "x-customer-id": self.customer_id,
        }

        async with websockets.connect(self.server_addr, extra_headers=request_headers) as ws:
            await ws.send(json.dumps({
                "config": {
                    "sample_rate": 16000,
                    "transaction_id": str(uuid.uuid4()),
                    "model": self.model,
                }
            }))

            while True:
                chunk = audio_buffer.read(chunk_size)
                if not chunk:
                    break

                await ws.send(chunk)

            await ws.send('{"eof": 1}')

            async for response in ws:
                response_data = json.loads(response)
                transcript_text = response_data.get("text", "")
                
                if transcript_text:
                    yield transcript_text

                if response_data.get("eos", False):
                    break

    async def transcribe(self, audio_file: str) -> str:
        with open(audio_file, "rb") as file:
            audio_buffer = io.BytesIO(file.read())
        
        full_transcription = ""
        async for partial_transcription in self.transcribe_stream(audio_buffer):
            full_transcription += partial_transcription + " "

        return full_transcription.strip()
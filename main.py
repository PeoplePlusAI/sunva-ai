from fastapi import FastAPI
from fastapi.responses import FileResponse
from core.api import stt, tts

app = FastAPI()

app.include_router(stt.router)
app.include_router(tts.router)

@app.get("/")
async def get():
    return FileResponse("static/index.html")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
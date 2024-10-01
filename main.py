from fastapi import FastAPI
from core.db.init_db import init_db, shutdown_db
from core.db.database import init_db, shutdown
from fastapi.responses import FileResponse
from core.api import stt, tts, user, language
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

origins = [
	"*"
    #"http://localhost:3000",  # Allow requests from your Next.js frontend
    # Add any other origins if needed
]

# Add the CORS middleware to the FastAPI application
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,  # List of allowed origins
    allow_credentials=True,  # Allow cookies to be sent
    allow_methods=["*"],  # Allow all HTTP methods (GET, POST, etc.)
    allow_headers=["*"],  # Allow all headers
)


app.include_router(stt.router)
app.include_router(tts.router)
app.include_router(user.router)
app.include_router(language.router)

@app.get("/")
async def get():
    return FileResponse("static/index.html")


@app.get("/is-alive")
def is_alive():
    return {"status": "alive"}

@app.on_event("startup")
async def on_startup():
    await init_db(3)

@app.on_event("shutdown")
async def on_shutdown():
    await shutdown()


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

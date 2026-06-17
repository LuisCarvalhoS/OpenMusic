from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.routers import audio

app = FastAPI(title="Open Music API", version="0.1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(audio.router)


@app.get("/")
def root() -> dict:
    return {"message": "Open Music API is running", "version": "0.1.0"}

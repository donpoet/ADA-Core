from fastapi import FastAPI
from app.api.routes import router
from fastapi.staticfiles import StaticFiles

app = FastAPI(
    title="ADA Core",
    version="0.2.0",
)
app.include_router(router)
app.mount("/static", StaticFiles(directory="web"), name="static")
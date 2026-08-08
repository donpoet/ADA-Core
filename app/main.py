from fastapi import FastAPI

app = FastAPI(
    title="ADA Core",
    version="0.1.0",
)

@app.get("/")
async def root():
    return {
        "name": "ADA Core", 
        "version": "0.1.0"
    }

@app.get("/health")
async def health():
    return {
        "status": "ok",
    }
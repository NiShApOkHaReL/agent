from fastapi import FastAPI
from app.api.routes import router
from app.config.settings import settings
from dotenv import load_dotenv
import uvicorn


load_dotenv()

app = FastAPI()
app.include_router(router, prefix="/api/v1")

if __name__ == "__main__":
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)

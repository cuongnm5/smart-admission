from dotenv import load_dotenv
load_dotenv()

from fastapi import FastAPI
import uvicorn

from app.api.routes_matching import router as matching_router
from app.api.routes_pipeline import router as pipeline_router
from app.api.routes_profile import router as profile_router
from app.core.logging import configure_logging
from fastapi.middleware.cors import CORSMiddleware

configure_logging()


origins = [
    "http://localhost.tiangolo.com",
    "https://localhost.tiangolo.com",
    "http://localhost",
    "http://localhost:8001",
    "http://localhost:8080",
    "http://localhost:8081",
]

app = FastAPI(title="Smart Admission - University Candidate Matching", version="1.0.0")
app.include_router(matching_router)
app.include_router(pipeline_router)
app.include_router(profile_router)
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)



@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)

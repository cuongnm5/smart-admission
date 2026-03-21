from fastapi import FastAPI
import uvicorn

from app.api.routes_matching import router as matching_router
from app.api.routes_pipeline import router as pipeline_router
from app.core.logging import configure_logging

configure_logging()

app = FastAPI(title="Smart Admission - University Candidate Matching", version="1.0.0")
app.include_router(matching_router)
app.include_router(pipeline_router)


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


if __name__ == "__main__":
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)

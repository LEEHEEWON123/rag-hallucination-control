from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from grounding_pipeline import health as pipeline_health

app = FastAPI(title="Grounding Guard API", version="0.1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health")
def health():
    return {
        "api": "ok",
        "pipeline": pipeline_health(),
    }

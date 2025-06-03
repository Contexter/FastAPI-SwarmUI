# app/main.py

from fastapi import FastAPI
from sqlmodel import SQLModel
from fastapi.openapi.utils import get_openapi

from app.models import engine
from app.routers import orchestrator, clientgen

app = FastAPI(
    title="FountainAI Orchestrator API",
    version="1.0.0",
    # We deliberately omit openapi_url/docs_url so that
    # FastAPI serves at the defaults: /openapi.json and /docs
)

@app.on_event("startup")
def on_startup():
    # Create all tables on startup
    SQLModel.metadata.create_all(engine)

# Mount both routers under /v1 exactly as before
app.include_router(orchestrator.router, prefix="/v1")
app.include_router(clientgen.router, prefix="/v1")


def custom_openapi():
    """
    Override the generated OpenAPI schema so that:
      • openapi version = "3.1.0"
      • servers = [{"url":"https://fountain.coach"}]
      • everything else is taken from FastAPI’s auto‐generated schema
    """
    if app.openapi_schema:
        return app.openapi_schema

    openapi_schema = get_openapi(
        title=app.title,
        version=app.version,
        routes=app.routes,
    )

    # Force OpenAPI version to 3.1.0
    openapi_schema["openapi"] = "3.1.0"

    # Inject a single servers entry
    openapi_schema["servers"] = [{"url": "https://fountain.coach"}]

    app.openapi_schema = openapi_schema
    return app.openapi_schema


# Replace FastAPI’s default openapi() with our custom version
app.openapi = custom_openapi

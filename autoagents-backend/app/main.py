"""FastAPI application entrypoint."""

from dotenv import load_dotenv
from fastapi import FastAPI, Request, Response
from fastapi.middleware.cors import CORSMiddleware
import re
from pathlib import Path

from .db import connect_to_mongo, close_mongo_connection
from .routers import auth, projects, features, stories, diagrams, agent_legacy, status, visualizer, suggestions, feedback

# Load .env file from the backend directory (parent of app/)
env_path = Path(__file__).parent.parent / ".env"
if env_path.exists():
    load_dotenv(dotenv_path=env_path, override=True)
    import logging
    logging.getLogger(__name__).info(f"Loaded .env file from: {env_path}")
else:
    import logging
    logging.getLogger(__name__).warning(
        f".env file not found at {env_path}. "
        "Using system environment variables only."
    )
    load_dotenv()  # Fallback to default behavior

app = FastAPI(title="AutoAgents Backend")

_allowed_origins = {
    "http://localhost:4200",
    "http://127.0.0.1:4200",
}
_allowed_origin_pattern = re.compile(r"https?://localhost(:\d+)?$")

app.add_middleware(
    CORSMiddleware,
    allow_origins=list(_allowed_origins),
    allow_origin_regex=_allowed_origin_pattern.pattern,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


def _eligible_origin(origin: str | None) -> str | None:
    if not origin:
        return None
    if origin in _allowed_origins or _allowed_origin_pattern.fullmatch(origin):
        return origin
    return None


@app.middleware("http")
async def ensure_cors_headers(request: Request, call_next):
    origin = _eligible_origin(request.headers.get("origin"))

    if request.method == "OPTIONS" and origin:
        headers = {
            "Access-Control-Allow-Origin": origin,
            "Access-Control-Allow-Methods": request.headers.get(
                "access-control-request-method", "*"
            ),
            "Access-Control-Allow-Headers": request.headers.get(
                "access-control-request-headers", "*"
            ),
            "Access-Control-Allow-Credentials": "true",
            "Vary": "Origin",
        }
        return Response(status_code=204, headers=headers)

    response = await call_next(request)

    if origin:
        response.headers.setdefault("Access-Control-Allow-Origin", origin)
        response.headers.setdefault("Access-Control-Allow-Credentials", "true")
        response.headers.setdefault("Vary", "Origin")

    return response


@app.on_event("startup")
async def on_startup() -> None:
    await connect_to_mongo()


@app.on_event("shutdown")
async def on_shutdown() -> None:
    await close_mongo_connection()


app.include_router(auth.router)
app.include_router(projects.router)
app.include_router(features.router)
app.include_router(stories.router)
app.include_router(diagrams.router)
app.include_router(agent_legacy.router)
app.include_router(status.router)
app.include_router(visualizer.router)
app.include_router(suggestions.router)
app.include_router(feedback.router)


@app.get("/")
async def read_root() -> dict[str, str]:
    return {"message": "AutoAgents backend placeholder"}

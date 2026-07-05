from pathlib import Path

from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse

from app.config import get_settings
from app.models import ResearchRequest, ResearchResponse
from app.workflow import run_fallback_research, run_research

app = FastAPI(title="Agent Research Lab", version="0.1.0")
STATIC = Path(__file__).parent / "static"


@app.get("/", include_in_schema=False)
async def index() -> FileResponse:
    return FileResponse(STATIC / "index.html")


@app.get("/health")
async def health() -> dict[str, str]:
    return {"status": "ok"}


@app.post("/api/research", response_model=ResearchResponse)
async def research(request: ResearchRequest) -> ResearchResponse:
    if not get_settings().openai_api_key:
        raise HTTPException(status_code=503, detail="OPENAI_API_KEY is not configured.")
    try:
        result = await run_research(request.topic)
    except Exception as exc:
        error = str(exc).lower()
        if "insufficient_quota" in error or "error code: 429" in error:
            result = await run_fallback_research(request.topic)
        else:
            raise HTTPException(status_code=502, detail=f"Research workflow failed: {exc}") from exc
    return ResearchResponse(
        topic=request.topic,
        report=result["report"],
        sources=result["web_sources"] + result["academic_sources"],
        review=result["review"],
        revision_count=result["revision_count"],
    )

from pydantic import BaseModel, Field


class ResearchRequest(BaseModel):
    topic: str = Field(min_length=8, max_length=500)


class Source(BaseModel):
    title: str
    url: str
    snippet: str = ""
    year: int | None = None
    source_type: str


class ResearchResponse(BaseModel):
    topic: str
    report: str
    sources: list[Source]
    review: str
    revision_count: int


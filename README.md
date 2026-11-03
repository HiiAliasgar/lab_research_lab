# Agent Research Lab

A multi-agent research application built with FastAPI and LangGraph. It explores how a research question can be decomposed, investigated across web and academic sources, and assembled into a cited report.

## Research workflow

The application organizes work into four responsibilities:

1. **Research Lead** — breaks a broad question into focused research tasks.
2. **Web Scout** — gathers current information from web search results.
3. **Academic Analyst** — searches scholarly metadata through OpenAlex.
4. **Editor** — synthesizes findings, checks the draft and can request a revision.

The workflow includes a review loop so the report can be revised before completion.

## Main capabilities

- Multi-step research orchestration.
- Web and academic-source discovery.
- Source tracking and citation handling.
- Report synthesis and review.
- Browser-based interface with progress updates.
- FastAPI endpoints and interactive API documentation.

## Technology

| Layer | Tools |
|---|---|
| API | FastAPI, Uvicorn |
| Orchestration | LangGraph |
| Model provider | OpenAI API |
| Web discovery | DuckDuckGo HTML results |
| Academic discovery | OpenAlex API |
| Interface | HTML, CSS, JavaScript |
| Dependency management | uv |

## Run locally

Requirements: Python 3.10+, uv, and an OpenAI API key.

```powershell
git clone https://github.com/HiiAliasgar/lab_research_lab.git
cd lab_research_lab
Copy-Item .env.example .env
# Add OPENAI_API_KEY to .env
uv sync --extra dev
uv run uvicorn app.main:app --reload
```

Open the application at `http://127.0.0.1:8000`. API documentation is available at `http://127.0.0.1:8000/docs`.

## Workflow sketch

```text
Question
   |
Research Lead
   |
+-----------------------+
| Web Scout             |
| Academic Analyst      |
+-----------------------+
   |
Evidence synthesis
   |
Editor / review
   |       ^
   +-- revise
   |
Research report
```

## Project layout

```text
lab_research_lab/
├── app/
│   ├── main.py
│   ├── models.py
│   ├── workflow.py
│   ├── tools.py
│   ├── config.py
│   └── static/
├── tests/
├── .env.example
└── pyproject.toml
```

## Notes

Research output depends on source availability and model quality. Citations should be checked against the original sources before relying on a generated report.

[View source code](https://github.com/HiiAliasgar/lab_research_lab)

import operator
from typing import Annotated, Literal, TypedDict

from langchain_openai import ChatOpenAI
from langgraph.graph import END, START, StateGraph
from pydantic import BaseModel, Field

from app.config import get_settings
from app.models import Source
from app.tools import gather_all


class Plan(BaseModel):
    queries: list[str] = Field(min_length=2, max_length=4)
    report_sections: list[str] = Field(min_length=3, max_length=7)


class Review(BaseModel):
    passed: bool
    feedback: str


class ResearchState(TypedDict):
    topic: str
    queries: list[str]
    sections: list[str]
    web_sources: list[Source]
    academic_sources: list[Source]
    report: str
    review: str
    review_passed: bool
    review_attempts: int
    revision_count: int
    events: Annotated[list[str], operator.add]


def _llm() -> ChatOpenAI:
    settings = get_settings()
    return ChatOpenAI(model=settings.openai_model, temperature=0.2, api_key=settings.openai_api_key)


async def planner(state: ResearchState) -> dict:
    prompt = (
        "You are a research lead. Decompose the topic into 2-4 precise search "
        "queries and define 3-7 useful report sections. Include a query focused "
        f"on recent developments. Topic: {state['topic']}"
    )
    plan = await _llm().with_structured_output(Plan).ainvoke(prompt)
    return {"queries": plan.queries, "sections": plan.report_sections, "events": ["Research plan created"]}


async def researchers(state: ResearchState) -> dict:
    web, academic = await gather_all(state["queries"], get_settings().max_search_results)
    return {
        "web_sources": web,
        "academic_sources": academic,
        "events": [f"Collected {len(web)} web and {len(academic)} academic sources"],
    }


def _evidence(sources: list[Source]) -> str:
    return "\n".join(
        f"[{index}] {source.title} ({source.year or 'n.d.'})\n"
        f"URL: {source.url}\nEvidence: {source.snippet}"
        for index, source in enumerate(sources, 1)
    )


async def synthesizer(state: ResearchState) -> dict:
    sources = state["web_sources"] + state["academic_sources"]
    feedback = state.get("review", "")
    prompt = f"""You are a senior research analyst. Write a rigorous, readable report.

Topic: {state['topic']}
Required sections: {', '.join(state['sections'])}
Reviewer feedback from a prior draft: {feedback or 'None'}

Evidence:
{_evidence(sources)}

Rules:
- Use Markdown with a title, executive summary, required sections, and conclusion.
- Cite factual claims inline with bracketed source numbers such as [2].
- Clearly separate established evidence, emerging signals, and uncertainty.
- Do not invent facts or citations. Only use the evidence supplied.
- End with a "Sources" section listing cited title and URL.
"""
    response = await _llm().ainvoke(prompt)
    return {"report": str(response.content), "events": ["Report synthesized"]}


async def reviewer(state: ResearchState) -> dict:
    prompt = f"""Act as a strict research editor. Review this report on:
1. coverage of the requested topic,
2. traceability of claims to citations,
3. balance between academic and current web evidence,
4. explicit uncertainty and limitations.

Pass it if it is publication-ready. If it fails, give concise, actionable feedback.
Topic: {state['topic']}
Report:
{state['report']}
"""
    result = await _llm().with_structured_output(Review).ainvoke(prompt)
    return {
        "review": result.feedback,
        "review_passed": result.passed,
        "review_attempts": state.get("review_attempts", 0) + 1,
        "revision_count": 1 if not result.passed and state.get("review_attempts", 0) == 0 else state.get("revision_count", 0),
        "events": ["Quality review passed" if result.passed else "Quality review requested a revision"],
    }


def route_review(state: ResearchState) -> Literal["revise", "done"]:
    return "revise" if not state["review_passed"] and state["review_attempts"] < 2 else "done"


def build_graph():
    graph = StateGraph(ResearchState)
    graph.add_node("planner", planner)
    graph.add_node("researchers", researchers)
    graph.add_node("synthesizer", synthesizer)
    graph.add_node("reviewer", reviewer)
    graph.add_edge(START, "planner")
    graph.add_edge("planner", "researchers")
    graph.add_edge("researchers", "synthesizer")
    graph.add_edge("synthesizer", "reviewer")
    graph.add_conditional_edges(
        "reviewer",
        route_review,
        {"revise": "synthesizer", "done": END},
    )
    return graph.compile()


research_graph = build_graph()


async def run_research(topic: str) -> ResearchState:
    initial: ResearchState = {
        "topic": topic,
        "queries": [],
        "sections": [],
        "web_sources": [],
        "academic_sources": [],
        "report": "",
        "review": "",
        "review_passed": False,
        "review_attempts": 0,
        "revision_count": 0,
        "events": [],
    }
    return await research_graph.ainvoke(initial)


async def run_fallback_research(topic: str) -> ResearchState:
    """Produce a source-grounded digest when the configured LLM is unavailable."""
    queries = [f"{topic} latest developments", f"{topic} review research"]
    web, academic = await gather_all(queries, get_settings().max_search_results)
    sources = web + academic

    def evidence_lines(items: list[Source], offset: int = 0) -> str:
        if not items:
            return "_No sources were returned by this collector._"
        return "\n".join(
            f"- **{source.title}** ({source.year or 'n.d.'}) — "
            f"{source.snippet or 'Source identified for further review.'} "
            f"[[{index + offset}]]({source.url})"
            for index, source in enumerate(items, 1)
        )

    source_list = "\n".join(
        f"{index}. [{source.title}]({source.url}) — {source.source_type}"
        for index, source in enumerate(sources, 1)
    )
    report = f"""# Evidence digest: {topic}

## Executive summary

This is a live, source-grounded evidence digest assembled by the web and
academic research agents. AI synthesis is temporarily unavailable because the
configured model account has no remaining quota, so the findings below preserve
source wording and avoid unsupported conclusions.

## Current web signals

{evidence_lines(web)}

## Academic evidence

{evidence_lines(academic, len(web))}

## Interpretation and limitations

These results are a discovery set, not a completed systematic review. Publication
quality, recency, methodology, and potential conflicts of interest should be
checked in the linked primary sources before making technical or commercial
decisions.

## Sources

{source_list or "_No sources could be retrieved._"}
"""
    return {
        "topic": topic,
        "queries": queries,
        "sections": ["Current web signals", "Academic evidence", "Limitations"],
        "web_sources": web,
        "academic_sources": academic,
        "report": report,
        "review": "Fallback evidence digest used because the configured LLM quota is unavailable.",
        "review_passed": False,
        "review_attempts": 0,
        "revision_count": 0,
        "events": ["LLM unavailable", "Fallback evidence digest created"],
    }

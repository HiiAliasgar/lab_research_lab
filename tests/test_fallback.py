from app.workflow import run_fallback_research


async def test_fallback_builds_grounded_digest(monkeypatch) -> None:
    async def fake_gather(queries, limit):
        from app.models import Source

        return (
            [Source(title="Industry update", url="https://example.com/web", snippet="A current signal.", source_type="web")],
            [Source(title="Review paper", url="https://example.com/paper", snippet="A scholarly signal.", year=2025, source_type="academic")],
        )

    monkeypatch.setattr("app.workflow.gather_all", fake_gather)
    result = await run_fallback_research("solid-state batteries")

    assert "Industry update" in result["report"]
    assert "Review paper" in result["report"]
    assert len(result["web_sources"] + result["academic_sources"]) == 2

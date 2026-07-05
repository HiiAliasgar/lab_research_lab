# 🔬 Agent Research Lab

A sophisticated **multi-agent research system** built with LangGraph that transforms complex questions into comprehensive, citation-backed research reports. The system orchestrates specialized AI agents that collaborate seamlessly to gather, analyze, and synthesize evidence from both web and academic sources.

## 🎯 Overview

Agent Research Lab employs an intelligent four-agent team:
- **Research Lead** - Decomposes complex questions into actionable research tasks
- **Web Scout** - Searches current web sources for latest developments and industry signals
- **Academic Analyst** - Cross-references scholarly papers through OpenAlex API
- **Editor** - Synthesizes all evidence into a publication-ready report with quality review

## ✨ Features

- 🚀 **Multi-Agent Orchestration** - Parallel evidence collection for efficiency
- 📚 **Dual Source Integration** - Combines web and academic research seamlessly
- 📖 **Citation Management** - Automatic source tracking and reference handling
- 🔄 **Quality Review** - Built-in revision loop for accuracy assurance
- 🎨 **Modern UI** - Beautiful, responsive frontend with smooth animations
- ⚡ **Real-time Updates** - Live progress tracking during research
- 🔌 **REST API** - Easy integration with `/docs` endpoint documentation

## 🚀 Quick Start

### Prerequisites
- Python 3.10+
- OpenAI API key
- uv package manager

### Installation & Run

```powershell
cd D:\code\agent_research_lab
Copy-Item .env.example .env
# Add your OpenAI API key to .env
uv sync --extra dev
uv run uvicorn app.main:app --reload
```

Open **http://127.0.0.1:8000** in your browser to access the web interface.

API documentation available at **http://127.0.0.1:8000/docs** (Swagger UI)

## 📊 Agent Workflow

```text
START -> planner -> parallel evidence collectors -> synthesizer -> reviewer
                                                            ^          |
                                                            \-- revise-/
                                                                       |
                                                                      END
```

The search tools use DuckDuckGo's HTML results and the public OpenAlex API, so
no search-service API key is required. The LLM requires `OPENAI_API_KEY`.

## 🛠 Tech Stack

- **Framework**: FastAPI + Uvicorn
- **AI Orchestration**: LangGraph
- **LLM**: OpenAI GPT
- **Web Search**: DuckDuckGo API
- **Academic Search**: OpenAlex API
- **Frontend**: HTML5 + CSS3 + Vanilla JavaScript
- **Dependency Management**: uv

## 📁 Project Structure

```
agent_research_lab/
├── app/
│   ├── main.py          # FastAPI application
│   ├── models.py        # Data models
│   ├── workflow.py      # LangGraph workflow definition
│   ├── tools.py         # Search and utility tools
│   ├── config.py        # Configuration
│   └── static/
│       └── index.html   # Modern responsive UI
├── tests/               # Test suite
├── .env.example         # Environment template
├── pyproject.toml       # Project configuration
└── README.md           # This file
```

## 🎨 UI Features

- **Responsive Design** - Works seamlessly on desktop and mobile
- **Real-time Progress** - Watch agents work with animated status indicators
- **Evidence Ledger** - Complete citation history with source types
- **Markdown Rendering** - Beautiful formatted reports
- **Smooth Animations** - Modern interactions and transitions

## 📝 API Endpoints

- `POST /api/research` - Submit a research topic and get a report
- `GET /docs` - Interactive Swagger documentation
- `GET /` - Serve the web interface

## 🤝 Contributing

Feel free to fork, modify, and submit pull requests. This is a research project showcasing multi-agent AI orchestration patterns.

## 📄 License

Open source - feel free to use and modify

## 🔗 References

- [LangGraph Documentation](https://langchain-ai.github.io/langgraph/)
- [OpenAI API](https://platform.openai.com/docs)
- [OpenAlex API](https://openalex.org/)

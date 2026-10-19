# Smart AI Agent — Full Specs & Production Code (Rebuilt Oct 2026)

## Overview
Production-ready LangGraph + Chainlit/Dash agent for CryptoMentions and business tools.  
Rebuilt cleanly from the original June 2026 specs.

## Key Features
- ReAct-style agent with Tavily web search + calculator tools
- SQLite checkpointer for persistent memory (swap to PostgreSQL for production)
- Chainlit chat UI (streaming, sessions)
- Dash interactive dashboard with chat history
- Centralized config + .env
- Docker + HF Spaces / Render / Railway deployment ready
- LangSmith tracing support
- Input sanitization basics + API key handling
- Easy extension points for CoinGecko, janitorial lead gen, LeadForge, etc.

## Files
- `requirements.txt`
- `config.py`
- `agent.py`
- `app_chainlit.py`
- `app_dash.py`
- `Dockerfile`
- `README.md`

## Quick Start
```bash
python -m venv venv && source venv/bin/activate
pip install -r requirements.txt
# Create .env with OPENAI_API_KEY, TAVILY_API_KEY, LANGCHAIN_API_KEY
chainlit run app_chainlit.py -w --port 8000 --host 0.0.0.0
# Dash: python app_dash.py
```

## Deployment
- Hugging Face Spaces (Docker)
- Render / Railway (GitHub auto-deploy)
- Docker self-host

## Next Features (Ready to Add)
- CoinGecko crypto tools
- Janitorial / LeadForge business tools
- PostgreSQL + Redis
- Multi-tenant auth
- Eval suite
- FastAPI backend

---
All source files are available in the accompanying project folder on Drive.

# Smart AI Agent
Production-ready LangGraph + Chainlit/Dash agent for CryptoMentions and business tools.

## Setup
```bash
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

Create `.env`:
```
OPENAI_API_KEY=your_key
TAVILY_API_KEY=your_key
LANGCHAIN_API_KEY=your_key
LANGCHAIN_PROJECT=crypto-mentions-agent
LANGCHAIN_TRACING_V2=true
```

## Run
- Chainlit: `chainlit run app_chainlit.py -w --port 8000 --host 0.0.0.0`
- Dash: `python app_dash.py`

## Features
- ReAct agent with Tavily search + calculator
- SQLite memory (swap to Postgres for prod)
- Chainlit chat UI + Dash dashboard
- Docker ready
- LangSmith tracing support
- Easy to extend with CoinGecko, janitorial lead gen, etc.

## Deployment
- Hugging Face Spaces (Docker)
- Render / Railway
- Self-host: `docker build -t crypto-agent . && docker run -p 8000:8000 --env-file .env crypto-agent`

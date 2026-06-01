# Chatbot Backend Template

Production-ready WhatsApp chatbot backend template for rapid client deployment.

## What This Is

A modular, config-driven FastAPI backend that:

- ✅ Handles WhatsApp messages via Gupshup webhooks
- ✅ Orchestrates OpenAI LLM with tool calling
- ✅ Manages conversation history in MongoDB
- ✅ Supports vector search (Pinecone KB)
- ✅ Dispatches formatted WhatsApp responses
- ✅ Extensible for any external APIs

**Boilerplate Code:** ~70% (reused across projects)  
**Client-Specific Code:** ~30% (prompts, flows, API adapters)

---

## Quick Start: Onboard a New Client

### 1. Copy & customize client config

```bash
cp config/client.config.example.yaml config/client.config.yaml
cp example.env .env
```

Edit `.env` with your:

- OpenAI API key
- MongoDB connection string
- Gupshup credentials (WhatsApp setup)
- Any external API keys

Edit `config/client.config.yaml` with your:

- System prompts (how bot behaves)
- Tools/flows (what the bot can do)
- External API endpoints
- Response templates

### 2. Install dependencies

```bash
pip install -r requirements.txt
pre-commit install
```

### 3. Run locally

```bash
uvicorn src.gateway.main:app --reload --port 8000
```

Test webhook:

```bash
curl -X POST http://localhost:8000/gupshup/message/hc \
  -H "Content-Type: application/json" \
  -d '{"type": "message", "payload": {"source": "919999999999", "type": "text", "text": "Hi"}}'
```

### 4. Run with Docker Compose

```bash
docker-compose up --build
```

This starts MongoDB + chatbot backend together.

### 5. Deploy

```bash
docker build -t chatbot-backend .
docker run -p 8000:8000 --env-file .env chatbot-backend
```

---

## File Guide: What to Modify Per Client

### ✅ You MUST modify:

- `config/client.config.yaml` - Prompts, tools, flows
- `.env` - All credentials and endpoints
- `src/router/message_router.py` - Intent routing logic (if needed)
- `src/ai/llm_orchestrator.py` - Tool execution (if using custom tools)
- Add client-specific files in `src/adapters/` for external APIs

### ❌ Do NOT modify:

- `src/gateway/main.py` - FastAPI setup
- `src/precheck/` - Webhook parsing
- `src/adapters/openai_adapter.py` - LLM calling
- `src/adapters/mongo_adapter.py` - Database logic
- `src/adapters/gupshup_adapter.py` - WhatsApp API
- `src/response/` - Message dispatch
- `src/utils/` - Logging, environment loading

---

## Architecture

```
User Message (WhatsApp)
    ↓
Gupshup Webhook → /gupshup/message/hc
    ↓
Duplicate Check → Session Fetch
    ↓
Message Router → [CLIENT-SPECIFIC] Intent detection
    ↓
LLM Orchestrator → Call OpenAI with tools
    ↓
Tool Execution → [CLIENT-SPECIFIC] API calls
    ↓
Response Builder → WhatsApp format
    ↓
Gupshup Send → User receives message
    ↓
Save to MongoDB chat history
```

---

## Environment Variables

Required:

```
OPENAI_API_KEY           # OpenAI API key
MONGO_URI                # MongoDB connection
GUPSHUP_API_KEY          # WhatsApp provider
GUPSHUP_APP_NAME         # Your WhatsApp business name
GUPSHUP_SOURCE           # Your WhatsApp number
```

Optional:

```
PINECONE_API              # Vector DB for knowledge base
CORS_ORIGINS              # Comma-separated allowed origins
APP_TITLE                 # App name for logs
ENV_MODE                  # dev or prod
LOG_DIR                   # Where to save logs
```

---

## Production Checklist

- [ ] `.env` filled with real credentials
- [ ] `config/client.config.yaml` customized
- [ ] System prompt tested & approved
- [ ] External APIs tested & working
- [ ] MongoDB indexes created
- [ ] Error monitoring set up (e.g., Sentry)
- [ ] Logs stored securely
- [ ] Rate limiting configured
- [ ] Load testing done
- [ ] Deployed to cloud (Vercel, Railway, Render, etc)

---

## Support

For questions, check:

1. `config/client.config.example.yaml` - Config reference
2. `example.env` - Environment reference
3. File comments - Each file marked with `[BOILERPLATE]`, `[CONFIG-DRIVEN]`, or `[CLIENT-SPECIFIC]`

---

## License

MIT

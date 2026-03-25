# Nextdot AI Agent — Premium Agentic Pipeline

**Live Demo**: [https://nextdot-agent.vercel.app/](https://nextdot-agent.vercel.app/)

A 4-step agentic pipeline that takes a raw customer message and produces:

1. **Classification** — intent + sentiment + language detection
2. **Structured extraction** — name, issue type, urgency, recommended action (JSON)
3. **Customer reply** — tone-matched, non-generic, language-aware (Hindi/Hinglish)
4. **Model reasoning** — why it made those choices

Built for the Nextdot AI Engineering Internship Assignment (Summer 2026).

---

## Features

- **Free Claude Access** — Uses Puter.js to provide Claude (Sonnet 4.6) without requiring an API key.
- **Multi-model support** — Claude (via Puter), Gemini (via API), and OpenAI (GPT-4o-mini), with side-by-side comparison mode
- **Edge case handling** — empty input, single-word messages, gibberish
- **Multilingual** — detects and responds in Hindi/Hinglish when needed
- **Premium Dashboard** — Next.js 16 interactive interface with glassmorphic design and history
- **CLI** — flexible flags for model selection and custom messages

---

## Setup

### 1. Clone the repo
```bash
git clone https://github.com/YOUR_USERNAME/nextdot-agent.git
cd nextdot-agent
```

### 2. Install dependencies
```bash
pip install -r requirements.txt
```

### 3. Add API keys
```bash
cp .env.example .env
# Edit .env — add at least one key (both enables comparison mode)
```

Get keys here:
- Anthropic (Claude): https://console.anthropic.com/
- Google Gemini (free): https://aistudio.google.com/

---

## Run

### Option A: Premium Next.js Dashboard (Recommended)
This is the full-stack version featuring persistent history and a modern design.

1. **Start Backend**:
   ```bash
   python server.py
   ```
2. **Start Frontend**:
   ```bash
   cd frontend
   npm run dev
   ```
3. Open `http://localhost:3000`

### Option B: Streamlit UI (Quick View)
```bash
streamlit run app.py
```

### Option C: CLI — Sample inputs
```bash
python agent.py                    # Run A/B/C with Claude
python agent.py --compare          # Both models side-by-side
```

---

## Output format

Each run produces a structured JSON file in `/outputs/`:

```json
{
  "label": "Input_A",
  "model": "claude-sonnet-4-20250514",
  "input_message": "...",
  "classification": {
    "intent": "complaint",
    "sentiment": "urgent",
    "language": "english"
  },
  "extracted_fields": {
    "customer_name": "Rohan Mehta",
    "issue_type": "billing / account access",
    "urgency_level": "Critical",
    "recommended_action": "..."
  },
  "reply": "...",
  "reasoning": "...",
  "latency_seconds": 3.2
}
```

In `--compare` mode, the output wraps both models under `"claude"` and `"gemini"` keys.

---

## Project Structure

This repository is organized to separate the **Core AI Pipeline** from the **Bonus Interactive Features**:

```
nextdot-agent/
├── agent.py            # Core Pipeline (CLI entry point)
├── THINKING.md         # Design decisions & strategy
├── README.md           # Setup & instructions
├── requirements.txt    # Python dependencies
├── .env.example        # API Key template
├── outputs/            # Required JSON outputs (A, B, C)
├── frontend/           # Bonus: Next.js 16 Web Dashboard
└── dashboard/          # Bonus: Support Services
    ├── server.py       # FastAPI Backend
    ├── app.py          # Streamlit UI
    └── history.json    # Persistent run history
```

---

## Run

### Option A: Core CLI — Sample inputs (Recommended for Evaluation)
Runs the 3 required sample inputs and saves results to `outputs/`.
```bash
python agent.py --model openai
```

### Option B: Premium Next.js Dashboard (Bonus)
A full-stack implementation featuring persistent history and a modern design.

1. **Start Backend**:
   ```bash
   python dashboard/server.py
   ```
2. **Start Frontend**:
   ```bash
   cd frontend
   npm run dev
   ```
3. Open `http://localhost:3000`

### Option C: Streamlit UI (Bonus — Quick View)
```bash
streamlit run dashboard/app.py
```

---

## Design Decisions

- **Structural Organization**: Separated the core logic from the UI/Dashboard components to ensure evaluators can immediately focus on the AI engineering requirements (`agent.py`).
- **One prompt, four steps**: All four pipeline steps run in a single LLM call. This preserves cross-step context (tone in the reply is informed by sentiment from Step 1) and reduces latency.
- **Failover-Ready**: The system is designed to gracefully switch between Claude, Gemini, and OpenAI based on available API keys.
- **Language-Aware**: Detects and responds in Hindi/Hinglish when appropriate, using zero hardcoded rules.

See [THINKING.md](./THINKING.md) for full reasoning.

# Nextdot AI Agent — Mini Pipeline That Thinks Out Loud

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

## Project structure

```
nextdot-agent/
├── agent.py          # Core pipeline (CLI entry point)
├── app.py            # Streamlit UI
├── requirements.txt
├── .env.example      # Template for API keys
├── .gitignore        # Excludes .env
├── README.md
├── THINKING.md
└── outputs/
    ├── output_A.json
    ├── output_B.json
    └── output_C.json
```

---

## Design decisions

- **One prompt, four steps**: All four pipeline steps run in a single LLM call per model. This preserves cross-step context (tone in the reply is informed by sentiment from Step 1) and reduces latency and cost.
- **No hardcoding**: Classification, extraction, reply, and reasoning are entirely model-driven. Zero if/else logic for the actual intelligence.
- **Graceful degradation**: If only one API key is present, the other model is skipped cleanly with a message rather than crashing.
- **Language-aware**: The system prompt and extraction explicitly ask for language detection, and the reply prompt instructs the model to respond in the detected language.

See [THINKING.md](./THINKING.md) for full reasoning on model choice, prompting strategy, and what I'd improve.

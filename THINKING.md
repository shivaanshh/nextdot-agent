# THINKING.md — Nextdot AI Agent Assignment

## Which models and why?

I used **Claude claude-sonnet-4-20250514** (Anthropic) as the primary model and **Gemini 2.0 Flash** (Google) for comparison. Claude was my first choice because it handles strict structured output — the four-section format with embedded JSON — with very few formatting failures. Gemini 2.0 Flash was the natural second choice for comparison: it's fast, free-tier accessible, and genuinely different in its reasoning style, which makes side-by-side comparison interesting rather than redundant.

## Prompting strategy

The core decision was **one prompt, four steps** — rather than four separate API calls chained together. This has two real advantages: it preserves cross-step context (the reply tone in Step 3 is directly informed by the sentiment detected in Step 1, without me having to pass it explicitly), and it's faster and cheaper. The tradeoff is that a long output is harder to parse if the model drifts from the format — which I mitigated with a rigid section-header structure (`CLASSIFICATION:`, `EXTRACTED_JSON:`, `REPLY:`, `REASONING:`).

I deliberately made the constraints in the prompt explicit and restrictive: exact enum values for intent/sentiment/urgency, a strict instruction not to write generic replies, and an explicit language-awareness rule for Hindi/Hinglish. Vague prompts produce vague outputs.

## What broke and how I fixed it

Two things broke during testing:

1. **Markdown fences around JSON**: Both models occasionally wrapped the JSON block in ` ```json ... ``` `. Fixed with a `.replace()` strip before `json.loads()`.
2. **REASONING cut off**: Early versions placed REASONING before REPLY in the format. The model would sometimes truncate the reply mid-sentence when reasoning followed immediately. Moving REASONING to the end fixed this completely.

Edge case handling (empty input, single-word messages) was added after I noticed the model would just hang or produce odd output with no graceful fallback. The validator now flags these before the API call, and the system prompt explicitly instructs the model how to handle them.

## The Upgrade: Why Next.js + FastAPI?

While the initial Streamlit app was functional, I decided to upgrade the UI to a **Next.js 14+ dashboard with a FastAPI backend**. This move was made to demonstrate "production-ready" thinking:
1. **Visual Excellence**: Next.js (with Tailwind and Framer Motion) allows for a significantly more premium, "wowed" user experience that standard Python-only UI frameworks can't match.
2. **Persistence**: Added a `history.json` and a session-based sidebar to track past analyses, making the tool feel like a real support workstation rather than a one-off demo.
3. **Architecture**: Decoupling the LLM logic (FastAPI) from the presentation layer (Next.js) is how modern AI products are actually built at Nextdot.

## Multi-Model Support (Claude, Gemini, OpenAI via Puter.js)

The system now supports three major AI families, providing a robust comparison tool:
- **Claude (v3.5 Sonnet)**: Primary for complex reasoning and Hindi.
- **Gemini (v2.0 Flash)**: Fast, modern reasoning style.
- **OpenAI (v5.4 / GPT-5.4)**: Integrated via Puter.js for frontend-first processing.

### Why Puter.js for All Models?

A major pivot during development was moving **all model processing to the frontend** using **Puter.js**. 

1. **User-Pays Model**: This allows the application to scale without the developer needing to maintain expensive backend API keys. Each user interacts with the models via their own browser session.
2. **Simplified Deployment**: By moving AI calls to the frontend, we avoid complex secrets management in the backend (no more `OPENAI_API_KEY` errors on Render). 
3. **Frontend Resilience**: This architecture makes the dashboard a true "Static Web App" that can be hosted on a CDN (Vercel) while still performing heavy-duty AI tasks.

## Security & Deployment Architecture

1. **Secret Scanning**: Implemented strict `.gitignore` rules for `.env` and `outputs/`. When an accidental key leak was detected by GitHub's Push Protection, I used `git commit --amend` and a full repository re-initialization to **purge the secrets from the history** before successfully pushing.
2. **Dual-Platform Ready**: 
   - **Frontend (Next.js)**: Deployed to **Vercel** with a custom `Root Directory` set to `frontend`.
   - **Backend (FastAPI)**: Deployed to **Render** to handle history persistence and CORS headers, using dynamic `PORT` allocation.

## What I'd improve with more time

- **Authentication**: Add a login layer for support leads vs. junior agents.
- **Vector Search (RAG)**: Use a vector DB (like ChromaDB) to find "similar past cases" and suggest how other agents resolved them.
- **Streaming UI**: Implement a more dynamic "typing" effect for the reasoning results as they come in from Puter.js.
- **Unit Tests**: Add comprehensive tests for the parsing logic using `pytest` for the backend and `Vitest` for the frontend.

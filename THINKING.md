# THINKING.md — Nextdot AI Agent Assignment

## Model Choice & Rationale
I chose **Claude 3.5 Sonnet** as the primary engine for this project due to its industry-leading precision in structured extraction and empathetic tone. **GPT-4o-mini** and **Gemini 2.0 Flash** serve as capable secondary failovers for high-volume scenarios. This multi-model approach ensure zero downtime and consistency. For the **live web dashboard** ([nextdot-agent.vercel.app](https://nextdot-agent.vercel.app/)), I integrated **Puter.js**, enabling a "user-pays" model that removes the need for developer-side API keys in a production environment.

## Prompting Strategy: "One Prompt, Four Steps"
Rather than chaining multiple API calls, I designed a single, highly structured system prompt. This strategy:
1. **Preserves Context**: The model "sees" the sentiment it just detected while writing the reply, ensuring perfect tone alignment.
2. **Reduces Latency**: Eliminates the overhead of sequential round-trips to the LLM.
3. **Structured Recovery**: Used rigid block headers (e.g., `EXTRACTED_JSON:`) allowed me to implement a robust Python parser that can handle minor LLM formatting drifts.

## Challenges & Solutions
- **The JSON Drift**: Early iterations sometimes included prose inside the JSON block. I fixed this by adding a "must be valid JSON, no prose" constraint in the prompt and implementing a markdown-aware parser in `agent.py`.
- **Secret Management**: I implemented a strict `.env` pattern for all sensitive keys, ensuring they are excluded from the repository via `.gitignore` while providing a redacted `.env.example` to ensure smooth and secure onboarding for other developers.

## Future Improvements
- **RAG Integration**: Use Vector Search to match current complaints with "similar resolved cases" to provide even more accurate recommended actions.
- **Streaming Logic**: Implement real-time token streaming in the dashboard to make the "thinking" process visible to the user.
- **Unit Testing**: Add `pytest` coverage for the parsing logic to ensure long-term pipeline stability.

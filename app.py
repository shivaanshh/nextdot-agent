"""
Nextdot AI Agent — Streamlit Interface
Run: streamlit run app.py
"""

import streamlit as st
import json
import time
import os
from dotenv import load_dotenv

load_dotenv()

# ─── Page config ─────────────────────────────────────────────────────────────

st.set_page_config(
    page_title="Nextdot AI Agent",
    page_icon="⚡",
    layout="wide"
)

st.markdown("""
<style>
    .main { background-color: #0d1117; }
    .block-container { padding-top: 2rem; }
    .stTextArea textarea { font-size: 0.9rem; }
    .badge {
        display: inline-block;
        padding: 2px 10px;
        border-radius: 12px;
        font-size: 0.8rem;
        font-weight: 600;
        margin-right: 6px;
    }
    .metric-box {
        background: #161b22;
        border: 1px solid #30363d;
        border-radius: 8px;
        padding: 12px 16px;
        margin-bottom: 8px;
    }
</style>
""", unsafe_allow_html=True)

# ─── Import pipeline ─────────────────────────────────────────────────────────

from agent import run_pipeline, CLAUDE_AVAILABLE, GEMINI_AVAILABLE, SAMPLE_INPUTS

# ─── Sidebar ─────────────────────────────────────────────────────────────────

with st.sidebar:
    st.title("⚡ Nextdot Agent")
    st.caption("Mini AI Agent — Thinks Out Loud")
    st.divider()

    st.subheader("Model")
    available_models = []
    if CLAUDE_AVAILABLE:
        available_models.append("Claude (claude-sonnet-4)")
    if GEMINI_AVAILABLE:
        available_models.append("Gemini (2.0 Flash)")
    if CLAUDE_AVAILABLE and GEMINI_AVAILABLE:
        available_models.append("Both (Compare)")

    if not available_models:
        st.error("No API keys found. Add ANTHROPIC_API_KEY or GEMINI_API_KEY to .env")
        st.stop()

    model_choice = st.radio("Select model", available_models)
    model_key = (
        "both" if "Both" in model_choice
        else "gemini" if "Gemini" in model_choice
        else "claude"
    )

    st.divider()
    st.subheader("Sample Inputs")
    sample_labels = {
        "A — Angry Customer": "A",
        "B — Curious Query": "B",
        "C — Positive Feedback": "C",
        "D — Hindi/Hinglish": "D",
        "E — Empty Input": "E",
        "F — Single Word": "F",
    }
    if st.button("Load Sample A"):
        st.session_state["prefill"] = SAMPLE_INPUTS["A"]
    if st.button("Load Sample B"):
        st.session_state["prefill"] = SAMPLE_INPUTS["B"]
    if st.button("Load Sample C"):
        st.session_state["prefill"] = SAMPLE_INPUTS["C"]
    if st.button("Load Hindi Sample"):
        st.session_state["prefill"] = SAMPLE_INPUTS["D"]

    st.divider()
    st.caption("Keys configured:")
    st.caption(f"{'✅' if CLAUDE_AVAILABLE else '❌'} Anthropic")
    st.caption(f"{'✅' if GEMINI_AVAILABLE else '❌'} Gemini")

# ─── Main UI ─────────────────────────────────────────────────────────────────

st.title("Mini AI Agent — Thinks Out Loud")
st.caption("Pipeline: Classify → Extract → Reply → Reason")

prefill = st.session_state.get("prefill", "")
message = st.text_area(
    "Customer Message",
    value=prefill,
    height=120,
    placeholder="Paste any customer message here — complaint, query, feedback, Hindi, Hinglish, or even empty..."
)

col1, col2 = st.columns([1, 5])
with col1:
    run = st.button("▶ Run Pipeline", type="primary", use_container_width=True)

if run:
    if not message.strip() and model_key != "both":
        st.warning("Message is empty — running anyway to demonstrate edge case handling.")

    with st.spinner("Running pipeline..."):
        t0 = time.time()
        result = run_pipeline(message, label="streamlit_run", model=model_key)
        total = round(time.time() - t0, 2)

    # ── Render results ─────────────────────────────────────────────────────

    def render_result(r: dict, title: str = None):
        if title:
            st.subheader(title)

        if "error" in r and not r.get("classification"):
            st.error(r["error"])
            return

        cls = r.get("classification", {})
        ex  = r.get("extracted_fields", {})

        # Classification badges
        intent    = cls.get("intent", "—")
        sentiment = cls.get("sentiment", "—")
        language  = cls.get("language", "—")

        COLORS = {
            "complaint": "#ff7b72", "query": "#79c0ff", "feedback": "#56d364",
            "request": "#e3b341", "unclear": "#8b949e",
            "urgent": "#ff7b72", "negative": "#f85149", "positive": "#56d364", "neutral": "#8b949e",
        }

        def badge(text, color="#58a6ff"):
            return f'<span class="badge" style="background:{color}22;color:{color};border:1px solid {color}44">{text}</span>'

        badges_html = (
            badge(intent,    COLORS.get(intent, "#58a6ff")) +
            badge(sentiment, COLORS.get(sentiment, "#58a6ff")) +
            badge(language,  "#a371f7")
        )

        c1, c2 = st.columns(2)

        with c1:
            st.markdown("**Step 1 — Classification**")
            st.markdown(badges_html, unsafe_allow_html=True)

            st.markdown("**Step 2 — Extracted Fields**")
            st.markdown(f"""
<div class="metric-box">
  <b>Name</b>: {ex.get("customer_name") or "<i>not provided</i>"}<br>
  <b>Issue</b>: {ex.get("issue_type", "—")}<br>
  <b>Urgency</b>: {ex.get("urgency_level", "—")}<br>
  <b>Action</b>: {ex.get("recommended_action", "—")}
</div>
""", unsafe_allow_html=True)

            with st.expander("Raw JSON"):
                st.json(ex)

        with c2:
            st.markdown("**Step 3 — Customer Reply**")
            st.info(r.get("reply", "—"))

            st.markdown("**Step 4 — Model Reasoning**")
            st.markdown(f"*{r.get('reasoning', '—')}*")

        if r.get("edge_case_flag"):
            st.warning(f"Edge case detected: `{r['edge_case_flag']}`")
        if r.get("latency_seconds"):
            st.caption(f"⏱ {r['latency_seconds']}s")
        if r.get("parse_error"):
            st.warning(f"Parse note: {r['parse_error']}")

    st.divider()

    if model_key == "both":
        col_c, col_g = st.columns(2)
        with col_c:
            render_result(result.get("claude", {}), "Claude claude-sonnet-4")
        with col_g:
            render_result(result.get("gemini", {}), "Gemini 2.0 Flash")
        st.caption(f"Total time: {total}s")
    else:
        render_result(result)
        st.caption(f"Total time: {total}s")

    # Download button
    st.divider()
    st.download_button(
        label="Download JSON",
        data=json.dumps(result, indent=2, ensure_ascii=False),
        file_name="nextdot_output.json",
        mime="application/json"
    )

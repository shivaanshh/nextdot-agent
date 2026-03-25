"""
Nextdot AI Intern Assignment — Mini AI Agent That Thinks Out Loud
Pipeline: Classify → Extract → Reply → Explain Reasoning

Supports:
  - Claude (claude-sonnet-4-20250514) via Anthropic SDK
  - Gemini Flash (gemini-2.0-flash) via Google Generative AI SDK
  - Dual-model comparison mode
  - Edge case handling (empty, too short, Hindi/Hinglish)
  - CLI with custom messages and model selection
"""

import os
import json
import sys
import time
from dotenv import load_dotenv

load_dotenv()

# ─── Optional imports (graceful degradation if a key is missing) ──────────────

try:
    import anthropic
    CLAUDE_CLIENT = anthropic.Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))
    CLAUDE_AVAILABLE = bool(os.getenv("ANTHROPIC_API_KEY"))
except Exception:
    CLAUDE_AVAILABLE = False
    CLAUDE_CLIENT = None

try:
    import google.generativeai as genai
    genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
    GEMINI_AVAILABLE = bool(os.getenv("GEMINI_API_KEY"))
except Exception:
    GEMINI_AVAILABLE = False

try:
    from openai import OpenAI
    OPENAI_CLIENT = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
    OPENAI_AVAILABLE = bool(os.getenv("OPENAI_API_KEY"))
except Exception:
    OPENAI_AVAILABLE = False
    OPENAI_CLIENT = None

CLAUDE_MODEL = "claude-sonnet-4-20250514"
GEMINI_MODEL = "gemini-2.0-flash"
OPENAI_MODEL = "gpt-4o-mini"


# ─── Prompts ──────────────────────────────────────────────────────────────────

SYSTEM_PROMPT = (
    "You are an intelligent customer support AI agent for Nextdot, "
    "an AI products company based in India. You analyze customer messages and respond "
    "with structured, empathetic, and professional output.\n\n"
    "Important:\n"
    "- Never use generic template responses. Every reply must be specific to the message.\n"
    "- If the message is in Hindi or Hinglish, reply in the SAME language.\n"
    "- If the message is empty, too short to understand, or gibberish, still return the "
    "full format but set intent to 'unclear', sentiment to 'neutral', urgency to 'Low', "
    "and reply asking the customer politely to elaborate."
)

PIPELINE_PROMPT = """Analyze the following customer message and complete ALL four steps.

CUSTOMER MESSAGE:
\"\"\"{message}\"\"\"

---

STEP 1 — CLASSIFY
Detect:
- intent: one of [complaint, query, feedback, request, unclear]
- sentiment: one of [positive, neutral, negative, urgent]
- language: one of [english, hindi, hinglish, other]

STEP 2 — EXTRACT (must be valid JSON, no prose)
Fields:
- customer_name: string or null
- issue_type: short label e.g. "billing", "product inquiry", "appreciation", "unclear"
- urgency_level: one of [Low, Medium, High, Critical]
- recommended_action: one specific action the support team should take

STEP 3 — GENERATE REPLY
Rules:
- Tone MUST match the detected sentiment (apologetic for urgent/negative, warm for positive, helpful for query)
- If language is hindi or hinglish, write the reply in Hindi/Hinglish
- Do NOT write a generic response — be specific to this message
- Address by name if available
- 3-5 sentences max

STEP 4 — EXPLAIN REASONING
3-5 sentences explaining: why this intent + sentiment, why this urgency level, why this tone.

---

Respond in EXACTLY this format:

CLASSIFICATION:
Intent: <value>
Sentiment: <value>
Language: <value>

EXTRACTED_JSON:
<valid JSON object>

REPLY:
<reply text>

REASONING:
<reasoning text>"""


# ─── Edge case detector ───────────────────────────────────────────────────────

def validate_message(message: str):
    """Returns (is_valid, edge_flag). Flags edge cases but still runs the pipeline."""
    if not message or not message.strip():
        return False, "empty"
    stripped = message.strip()
    if len(stripped) < 5:
        return True, "very_short"
    if len(stripped.split()) == 1:
        return True, "single_word"
    return True, "ok"


# ─── Parser ───────────────────────────────────────────────────────────────────

def parse_pipeline_output(raw_text: str, model_name: str, message: str, label: str) -> dict:
    """Parses structured LLM output into a clean Python dict."""
    result = {
        "id": f"msg_ {int(time.time() * 1000)}",
        "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "label": label,
        "model": model_name,
        "input_message": message,
        "classification": {"intent": "unclear", "sentiment": "neutral", "language": "english"},
        "extracted_fields": {},
        "reply": "",
        "reasoning": ""
    }

    try:
        # Improved parsing with normalized keys and block extraction
        if "CLASSIFICATION:" in raw_text:
            cls_block = raw_text.split("CLASSIFICATION:")[1].split("EXTRACTED_JSON:")[0].strip()
            for line in cls_block.splitlines():
                if ":" in line:
                    key, val = line.split(":", 1)
                    key = key.strip().lower()
                    if key in ["intent", "sentiment", "language"]:
                        classification = result.get("classification", {})
                        if isinstance(classification, dict):
                            classification[key] = val.strip()

        if "EXTRACTED_JSON:" in raw_text:
            json_block = raw_text.split("EXTRACTED_JSON:")[1].split("REPLY:")[0].strip()
            # Handle markdown fences if present
            if "```" in json_block:
                json_block = json_block.split("```")[1]
                if json_block.startswith("json"):
                    json_block = json_block[4:]
            result["extracted_fields"] = json.loads(json_block.strip())

        if "REPLY:" in raw_text:
            result["reply"] = raw_text.split("REPLY:")[1].split("REASONING:")[0].strip()

        if "REASONING:" in raw_text:
            result["reasoning"] = raw_text.split("REASONING:")[1].strip()

    except Exception as e:
        result["parse_error"] = str(e)
        # Fallback: if we have the reply but JSON failed, we still have something.
    
    return result


def get_history(history_file: str = "history.json") -> list:
    """Loads history from a JSON file."""
    if not os.path.exists(history_file):
        return []
    try:
        with open(history_file, "r", encoding="utf-8") as f:
            return json.load(f)
    except:
        return []


def save_to_history(data: dict, history_file: str = "history.json"):
    """Appends a new result to the history file."""
    history = get_history(history_file)
    history.insert(0, data)  # Newest first
    with open(history_file, "w", encoding="utf-8") as f:
        json.dump(history[:50], f, indent=2, ensure_ascii=False)  # Keep last 50


# ─── Model runners ────────────────────────────────────────────────────────────

def run_claude(message: str) -> str:
    """Calls Claude claude-sonnet-4-20250514 and returns raw response text."""
    if not CLAUDE_AVAILABLE:
        raise EnvironmentError("ANTHROPIC_API_KEY not set in .env")
    try:
        response = CLAUDE_CLIENT.messages.create(
            model=CLAUDE_MODEL,
            max_tokens=1500,
            system=SYSTEM_PROMPT,
            messages=[{"role": "user", "content": PIPELINE_PROMPT.format(message=message)}]
        )
        return response.content[0].text
    except Exception as e:
        if "429" in str(e) or "overloaded" in str(e).lower():
            raise RuntimeError("Claude API is currently busy or quota exceeded. Please try Gemini, OpenAI, or wait a minute.")
        raise e


def run_gemini(message: str) -> str:
    """Calls Gemini 2.0 Flash and returns raw response text."""
    if not GEMINI_AVAILABLE:
        raise EnvironmentError("GEMINI_API_KEY not set in .env")
    try:
        model = genai.GenerativeModel(
            model_name=GEMINI_MODEL,
            system_instruction=SYSTEM_PROMPT
        )
        response = model.generate_content(PIPELINE_PROMPT.format(message=message))
        return response.text
    except Exception as e:
        if "429" in str(e) or "quota" in str(e).lower():
            raise RuntimeError("Gemini Free Tier quota exceeded. This happens when too many requests are made too quickly. Please switch to OpenAI (GPT-4o) or wait 30 seconds.")
        raise e


def run_openai(message: str) -> str:
    """Calls OpenAI GPT-4o-mini and returns raw response text."""
    if not OPENAI_AVAILABLE:
        raise EnvironmentError("OPENAI_API_KEY not set in .env")
    try:
        response = OPENAI_CLIENT.chat.completions.create(
            model=OPENAI_MODEL,
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": PIPELINE_PROMPT.format(message=message)}
            ]
        )
        return response.choices[0].message.content
    except Exception as e:
        if "429" in str(e) or "insufficient_quota" in str(e).lower():
            raise RuntimeError("OpenAI API quota exceeded or billing issue. Please try Claude/Gemini or check your OpenAI dashboard.")
        raise e


# ─── Core pipeline ────────────────────────────────────────────────────────────

def run_pipeline(
    message: str,
    label: str = "input",
    model: str = "claude",
    save_output: bool = False,
    output_dir: str = "outputs"
) -> dict:
    """
    Runs the 4-step AI pipeline on a customer message.

    Args:
        message:     Raw customer message string.
        label:       Name for this run (used in filenames and output).
        model:       "claude", "gemini", or "both".
        save_output: If True, writes results to JSON file.
        output_dir:  Directory for output files.

    Returns:
        Parsed result dict. If model="both", returns {"claude": ..., "gemini": ...}.
    """
    is_valid, edge_flag = validate_message(message)

    if not is_valid:
        empty_result = {
            "label": label,
            "model": model,
            "input_message": message,
            "edge_case": "empty_input",
            "error": "Message is empty. Please provide a customer message.",
            "classification": {},
            "extracted_fields": {},
            "reply": "",
            "reasoning": ""
        }
        _print_result(empty_result)
        if save_output:
            os.makedirs(output_dir, exist_ok=True)
            _save(empty_result, label, output_dir)
        return empty_result

    msg = message.strip()
    _print_header(label, msg, edge_flag)

    results = {}
    models_to_run = []

    if model in ("claude", "both"):
        if CLAUDE_AVAILABLE:
            models_to_run.append(("claude", CLAUDE_MODEL, run_claude))
        else:
            print("  [SKIP] Claude — ANTHROPIC_API_KEY not found in .env")

    if model in ("gemini", "both"):
        if GEMINI_AVAILABLE:
            models_to_run.append(("gemini", GEMINI_MODEL, run_gemini))
        else:
            print("  [SKIP] Gemini — GEMINI_API_KEY not found in .env")

    if model in ("openai", "both"):
        if OPENAI_AVAILABLE:
            models_to_run.append(("openai", OPENAI_MODEL, run_openai))
        else:
            print("  [SKIP] OpenAI — OPENAI_API_KEY not found in .env")

    if not models_to_run:
        raise EnvironmentError(
            "No API keys configured. Add ANTHROPIC_API_KEY or GEMINI_API_KEY to .env"
        )

    for model_key, model_name, runner in models_to_run:
        print(f"\n  Running {model_name}...")
        t0 = time.time()
        try:
            raw = runner(msg)
            elapsed = round(time.time() - t0, 2)
            parsed = parse_pipeline_output(raw, model_name, msg, label)
            parsed["latency_seconds"] = elapsed
            if edge_flag != "ok":
                parsed["edge_case_flag"] = edge_flag
            results[model_key] = parsed
            _print_result(parsed)
        except Exception as e:
            results[model_key] = {"error": str(e), "model": model_name, "label": label}
            print(f"  [ERROR] {model_name}: {e}")

    if model == "both":
        final = results
    elif results:
        final = list(results.values())[0]
    else:
        final = {"error": "No model results produced", "label": label}

    if save_output:
        os.makedirs(output_dir, exist_ok=True)
        _save(final, label, output_dir)

    return final


def _save(data: dict, label: str, output_dir: str):
    suffix = label.replace(" ", "_").replace("/", "-")
    path = os.path.join(output_dir, f"output_{suffix}.json")
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    print(f"\n  Saved to {path}")


# ─── Pretty printer ───────────────────────────────────────────────────────────

def _print_header(label: str, message: str, edge_flag: str):
    print(f"\n{'='*62}")
    print(f"  {label}")
    print(f"{'='*62}")
    preview = message if len(message) < 80 else message[:77] + "..."
    print(f"  Input: \"{preview}\"")
    if edge_flag != "ok":
        print(f"  [Edge case: {edge_flag}]")


def _print_result(r: dict):
    if "error" in r and not r.get("classification"):
        print(f"  Error: {r['error']}")
        return
    cls = r.get("classification", {})
    ex  = r.get("extracted_fields", {})
    print(f"\n  CLASSIFICATION")
    print(f"    Intent    : {cls.get('intent', '-')}")
    print(f"    Sentiment : {cls.get('sentiment', '-')}")
    print(f"    Language  : {cls.get('language', '-')}")
    print(f"\n  EXTRACTED FIELDS")
    print(f"    Name      : {ex.get('customer_name') or '(not provided)'}")
    print(f"    Issue     : {ex.get('issue_type', '-')}")
    print(f"    Urgency   : {ex.get('urgency_level', '-')}")
    print(f"    Action    : {ex.get('recommended_action', '-')}")
    print(f"\n  REPLY")
    for line in r.get("reply", "").splitlines():
        print(f"    {line}")
    print(f"\n  REASONING")
    for line in r.get("reasoning", "").splitlines():
        print(f"    {line}")
    if "latency_seconds" in r:
        print(f"\n  [{r['latency_seconds']}s]")
    if "parse_error" in r:
        print(f"  [Parse warning: {r['parse_error']}]")


# ─── Sample inputs ────────────────────────────────────────────────────────────

SAMPLE_INPUTS = {
    "A": (
        "i ordered the premium plan 3 weeks ago and STILL havent received any confirmation "
        "email or access. this is absolutely ridiculous. i paid Rs 4999 and nobody has "
        "responded to my 4 emails. if this isnt fixed today im disputing the charge with my bank. "
        "my name is Rohan Mehta and my order id is ORD-8821."
    ),
    "B": (
        "hi I saw your AI tool on linkedin and I am curious how it works for small businesses? "
        "like do you guys offer any free trial or something? also can it work with whatsapp? "
        "just exploring options for now nothing urgent."
    ),
    "C": (
        "Just wanted to say the onboarding session last Tuesday was really well done. "
        "Priya from your team was super helpful and patient. The tool is working great so far. "
        "Looking forward to the advanced features you mentioned. Keep it up!"
    ),
    # Bonus edge cases
    "D": "kal maine aapke tool ka demo dekha, bahut accha laga! kya aap mujhe pricing bata sakte hain?",
    "E": "",
    "F": "help",
}


# ─── CLI ──────────────────────────────────────────────────────────────────────

def print_usage():
    print("""
Nextdot AI Agent — Usage:

  python agent.py                        Run samples A/B/C with Claude
  python agent.py --all                  Run all samples including edge cases (D/E/F)
  python agent.py --compare              Run A/B/C with both Claude + Gemini
  python agent.py --model gemini         Use Gemini for all samples
  python agent.py "your message"         Run a custom message with Claude
  python agent.py --model gemini "msg"   Run a custom message with Gemini
  python agent.py --help                 Show this help
""")


def main():
    os.makedirs("outputs", exist_ok=True)
    args = sys.argv[1:]

    model   = "claude"
    run_all = False
    compare = False
    custom  = None

    i = 0
    while i < len(args):
        if args[i] == "--model" and i + 1 < len(args):
            model = args[i + 1]; i += 2
        elif args[i] == "--all":
            run_all = True; i += 1
        elif args[i] == "--compare":
            compare = True; model = "both"; i += 1
        elif args[i] in ("--help", "-h"):
            print_usage(); return
        else:
            custom = " ".join(args[i:]); break

    if custom is not None:
        run_pipeline(custom, label="custom", model=model, save_output=True)
        return

    keys = list(SAMPLE_INPUTS.keys()) if run_all else ["A", "B", "C"]

    for key in keys:
        run_pipeline(
            SAMPLE_INPUTS[key],
            label=f"Input_{key}",
            model=model,
            save_output=True,
            output_dir="outputs"
        )

    print(f"\n{'='*62}")
    print("  All done. Outputs saved to /outputs/")
    print(f"{'='*62}\n")


if __name__ == "__main__":
    main()

// Use environment variable for the API URL in production, or fallback to the current host on port 8000 for local development
const API_BASE = process.env.NEXT_PUBLIC_API_URL || (typeof window !== "undefined" 
  ? `http://${window.location.hostname}:8000` 
  : "http://localhost:8000")

const SYSTEM_PROMPT = `You are an intelligent customer support AI agent for Nextdot, an AI products company based in India. You analyze customer messages and respond with structured, empathetic, and professional output.
Important:
- Never use generic template responses. Every reply must be specific to the message.
- If the message is in Hindi or Hinglish, reply in the SAME language.
- If the message is empty, too short to understand, or gibberish, still return the full format but set intent to 'unclear', sentiment to 'neutral', urgency to 'Low', and reply asking the customer politely to elaborate.`

const PIPELINE_PROMPT = `Analyze the following customer message and complete ALL four steps.

CUSTOMER MESSAGE:
"""{message}"""

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
<reasoning text>`

export type Classification = {
  intent: string
  sentiment: string
  language: string
}

export type ExtractedFields = {
  customer_name?: string
  issue_type?: string
  urgency_level?: string
  recommended_action?: string
  [key: string]: any
}

export type PipelineResult = {
  id: string
  timestamp: string
  label: string
  model: string
  input_message: string
  classification: Classification
  extracted_fields: ExtractedFields
  reply: string
  reasoning: string
  latency_seconds?: number
  parse_error?: string
  error?: string
}

export type ComparisonResult = {
  claude?: PipelineResult
  gemini?: PipelineResult
  openai?: PipelineResult
}

export async function processMessage(message: string, model: string = "claude"): Promise<PipelineResult | ComparisonResult> {
  const hasPuter = typeof window !== "undefined" && (window as any).puter;

  // Use Puter for Claude single model
  if (model === "claude" && hasPuter) {
    return processWithPuter(message)
  }

  // Use Puter for OpenAI single model
  if (model === "openai" && hasPuter) {
    return processWithPuterOpenAI(message)
  }

  // If "both", we can combine Puter (Claude/Gemini/OpenAI) 
  if (model === "both" && hasPuter) {
    const [claudeResult, geminiResult, openaiResult] = await Promise.all([
      processWithPuter(message),
      processWithPuterGemini(message),
      processWithPuterOpenAI(message)
    ]);
    
    return { 
      claude: claudeResult, 
      gemini: geminiResult,
      openai: openaiResult
    };
  }

  const res = await fetch(`${API_BASE}/process`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ message, model }),
  })

  if (!res.ok) {
    const err = await res.json()
    throw new Error(err.detail || "Failed to process message")
  }
  return res.json()
}

function parsePuterResponse(rawText: string, message: string, modelName: string): PipelineResult {
  const result: PipelineResult = {
    id: `msg_puter_${Date.now()}_${Math.random().toString(36).substr(2, 5)}`,
    timestamp: new Date().toISOString(),
    label: "puter_web",
    model: modelName,
    input_message: message,
    classification: { intent: "unclear", sentiment: "neutral", language: "english" },
    extracted_fields: {},
    reply: "",
    reasoning: ""
  }

  try {
    if (rawText.includes("CLASSIFICATION:")) {
      const clsBlock = rawText.split("CLASSIFICATION:")[1].split("EXTRACTED_JSON:")[0].trim()
      clsBlock.split('\n').forEach((line: string) => {
        if (line.includes(':')) {
           const [k, v] = line.split(':');
           const key = k.trim().toLowerCase();
           if (["intent", "sentiment", "language"].includes(key)) {
             (result.classification as any)[key] = v.trim();
           }
        }
      })
    }

    if (rawText.includes("EXTRACTED_JSON:")) {
      let jsonBlock = rawText.split("EXTRACTED_JSON:")[1].split("REPLY:")[0].trim()
      if (jsonBlock.includes("```")) {
        // Try to find the JSON block inside markdown
        const match = jsonBlock.match(/```(?:json)?\s*([\s\S]*?)\s*```/);
        if (match) jsonBlock = match[1];
        else jsonBlock = jsonBlock.replace(/```json\n?|\n?```/g, "").trim();
      }
      try {
        result.extracted_fields = JSON.parse(jsonBlock)
      } catch (je) {
        console.error("JSON parse error in Puter response:", je);
        result.extracted_fields = { error: "Failed to parse JSON", raw: jsonBlock };
      }
    }

    if (rawText.includes("REPLY:")) {
      result.reply = rawText.split("REPLY:")[1].split("REASONING:")[0].trim()
    }

    if (rawText.includes("REASONING:")) {
      result.reasoning = rawText.split("REASONING:")[1].trim()
    }
  } catch (e) {
    result.parse_error = String(e)
  }

  return result
}

async function processWithPuter(message: string): Promise<PipelineResult> {
  const fullPrompt = `${SYSTEM_PROMPT}\n\n${PIPELINE_PROMPT.replace('{message}', message)}`
  const response = await (window as any).puter.ai.chat(fullPrompt, { model: 'claude-sonnet-4-6' })
  const rawText = response.message.content[0].text
  return parsePuterResponse(rawText, message, "claude-sonnet-4-6 (Free)")
}

async function processWithPuterGemini(message: string): Promise<PipelineResult> {
  const fullPrompt = `${SYSTEM_PROMPT}\n\n${PIPELINE_PROMPT.replace('{message}', message)}`
  const response = await (window as any).puter.ai.chat(fullPrompt, { model: 'gemini-2.0-flash' })
  const rawText = typeof response === 'string' ? response : (response.message?.content?.[0]?.text || response.message?.content || response.text || "")
  return parsePuterResponse(rawText, message, "gemini-2.0-flash (Free Puter)")
}

async function processWithPuterOpenAI(message: string): Promise<PipelineResult> {
  const fullPrompt = `${SYSTEM_PROMPT}\n\n${PIPELINE_PROMPT.replace('{message}', message)}`
  // Using gpt-5.4-nano for free text generation as per docs
  const response = await (window as any).puter.ai.chat(fullPrompt, { model: 'gpt-5.4' })
  const rawText = typeof response === 'string' ? response : (response.message?.content?.[0]?.text || response.message?.content || response.text || "")
  return parsePuterResponse(rawText, message, "gpt-5.4 (Free Puter)")
}

export async function getHistory(): Promise<(PipelineResult | ComparisonResult)[]> {
  const res = await fetch(`${API_BASE}/history`)
  if (!res.ok) throw new Error("Failed to fetch history")
  return res.json()
}

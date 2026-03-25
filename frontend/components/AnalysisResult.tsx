'use client'

import React from 'react'
import { CheckCircle2, AlertCircle, Info, MessageSquare, Brain, Target, Search } from 'lucide-react'
import { cn } from '@/lib/utils'
import { PipelineResult } from '@/lib/api'

interface AnalysisResultProps {
  result: PipelineResult
  title?: string
}

const COLORS = {
  complaint: "bg-red-500/10 text-red-500 border-red-500/20",
  query: "bg-blue-500/10 text-blue-500 border-blue-500/20",
  feedback: "bg-green-500/10 text-green-500 border-green-500/20",
  request: "bg-yellow-500/10 text-yellow-500 border-yellow-500/20",
  unclear: "bg-zinc-500/10 text-zinc-500 border-zinc-500/20",
  urgent: "bg-red-500/10 text-red-500 border-red-500/20",
  negative: "bg-red-500/10 text-red-500 border-red-500/20",
  positive: "bg-green-500/10 text-green-500 border-green-500/20",
  neutral: "bg-zinc-500/10 text-zinc-500 border-zinc-500/20",
}

export default function AnalysisResult({ result, title }: AnalysisResultProps) {
  if (!result || result.error) {
    return (
      <div className="rounded-2xl border border-destructive/20 bg-destructive/5 p-6 backdrop-blur-sm">
        <div className="flex items-center gap-2 text-destructive mb-2">
          <AlertCircle className="h-5 w-5" />
          <span className="font-semibold">Error processing message</span>
        </div>
        <p className="text-muted-foreground text-sm">{result?.error || 'Unknown error occurred'}</p>
      </div>
    )
  }

  const { classification, extracted_fields, reply, reasoning } = result

  return (
    <div className="space-y-6 rounded-2xl border border-border bg-card/50 p-6 backdrop-blur-sm shadow-xl transition-all hover:bg-card/80">
      {title && (
        <div className="flex items-center justify-between border-b border-border pb-4">
          <h3 className="text-lg font-bold tracking-tight text-foreground">{title}</h3>
          <span className="text-[10px] uppercase tracking-widest text-muted-foreground font-bold bg-secondary px-2 py-1 rounded">
            {result.model}
          </span>
        </div>
      )}

      {/* Step 1: Classification */}
      <div className="space-y-3">
        <div className="flex items-center gap-2 text-xs font-bold uppercase tracking-widest text-muted-foreground">
          <Target className="h-3 w-3" /> Step 1 — Classification
        </div>
        <div className="flex flex-wrap gap-2">
          {Object.entries(classification).map(([key, value]) => (
            <div
              key={key}
              className={cn(
                "px-3 py-1 rounded-full text-[10px] font-bold uppercase tracking-wider border",
                COLORS[value as keyof typeof COLORS] || "bg-muted text-muted-foreground border-border"
              )}
            >
              <span className="opacity-50 mr-1.5">{key}:</span>
              {value}
            </div>
          ))}
        </div>
      </div>

      {/* Step 2: Extracted Fields */}
      <div className="space-y-3">
        <div className="flex items-center gap-2 text-xs font-bold uppercase tracking-widest text-muted-foreground">
          <Search className="h-3 w-3" /> Step 2 — Extracted Fields
        </div>
        <div className="grid grid-cols-1 gap-3">
          {Object.entries(extracted_fields).map(([key, value]) => (
            <div key={key} className="rounded-xl bg-secondary/50 border border-border p-3 flex flex-col gap-1">
              <span className="text-[10px] font-bold uppercase tracking-widest text-muted-foreground">
                {key.replace('_', ' ')}
              </span>
              <span className="text-sm text-foreground truncate">
                {String(value || 'N/A')}
              </span>
            </div>
          ))}
        </div>
      </div>

      {/* Step 3: Reply */}
      <div className="space-y-3">
        <div className="flex items-center gap-2 text-xs font-bold uppercase tracking-widest text-muted-foreground">
          <MessageSquare className="h-3 w-3" /> Step 3 — Customer Reply
        </div>
        <div className="relative rounded-xl bg-blue-500/5 dark:bg-blue-600/5 border border-blue-500/10 p-5 italic text-foreground leading-relaxed group transition-all hover:bg-blue-500/10">
          <div className="absolute -left-1.5 top-5 h-8 w-1 bg-blue-600 rounded-full" />
          "{reply}"
        </div>
      </div>

      {/* Step 4: Reasoning */}
      <div className="space-y-3">
        <div className="flex items-center gap-2 text-xs font-bold uppercase tracking-widest text-muted-foreground">
          <Brain className="h-3 w-3" /> Step 4 — Model Reasoning
        </div>
        <p className="text-sm text-muted-foreground bg-muted border border-border p-4 rounded-xl leading-relaxed italic">
          {reasoning}
        </p>
      </div>

      {result.latency_seconds && (
         <div className="pt-2 text-[10px] text-muted-foreground font-mono tracking-tighter">
            LATENCY: {result.latency_seconds}s
         </div>
      )}
    </div>
  )
}

'use client'

import React, { useState } from 'react'
import { Send, Sparkles, Loader2 } from 'lucide-react'
import { cn } from '@/lib/utils'

interface MessageInputProps {
  onProcess: (message: string, model: string) => void
  isLoading: boolean
}

export default function MessageInput({ onProcess, isLoading }: MessageInputProps) {
  const [message, setMessage] = useState('')
  const [model, setModel] = useState('claude')

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault()
    if (!message.trim() || isLoading) return
    onProcess(message, model)
  }

  return (
    <div className="rounded-2xl border border-white/5 bg-zinc-900/50 p-6 backdrop-blur-sm shadow-xl transition-all hover:bg-zinc-900/80">
      <form onSubmit={handleSubmit} className="space-y-4">
        <label className="text-xs font-semibold uppercase tracking-wider text-zinc-500">Customer Message</label>
        <textarea
          className="w-full min-h-[140px] rounded-xl bg-black/40 border border-white/10 p-4 text-zinc-100 placeholder:text-zinc-600 focus:outline-none focus:ring-2 focus:ring-blue-500/50 transition-all resize-none"
          placeholder="Paste customer message here (complaint, query, feedback...)"
          value={message}
          onChange={(e) => setMessage(e.target.value)}
        />
        
        <div className="flex flex-wrap items-center justify-between gap-4">
          <div className="flex bg-zinc-100 dark:bg-black/40 rounded-lg p-1 border border-zinc-200 dark:border-white/5">
            {['claude', 'openai', 'gemini', 'both'].map((m) => (
              <button
                key={m}
                type="button"
                className={cn(
                  "px-4 py-1.5 rounded-md text-sm font-medium transition-all duration-200 capitalize",
                  model === m 
                    ? "bg-blue-600 text-white shadow-lg" 
                    : "text-zinc-500 dark:text-zinc-500 hover:text-zinc-800 dark:hover:text-zinc-300"
                )}
                onClick={() => setModel(m)}
              >
                {m === 'both' ? 'Compare' : m}
              </button>
            ))}
          </div>

          <button
            type="submit"
            disabled={!message.trim() || isLoading}
            className={cn(
              "flex items-center gap-2 px-6 py-2.5 rounded-xl font-semibold transition-all duration-300",
              message.trim() && !isLoading 
                ? "bg-white text-black hover:scale-[1.02] active:scale-95 shadow-xl shadow-white/10" 
                : "bg-zinc-800 text-zinc-500 cursor-not-allowed"
            )}
          >
            {isLoading ? (
              <>
                <Loader2 className="h-4 w-4 animate-spin" />
                Processing...
              </>
            ) : (
              <>
                <Sparkles className="h-4 w-4" />
                Run Pipeline
              </>
            )}
          </button>
        </div>
      </form>
    </div>
  )
}

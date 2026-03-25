'use client'

import React, { useState, useEffect } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import { Sparkles, History as HistoryIcon, LayoutPanelLeft, ArrowRight } from 'lucide-react'
import MessageInput from '@/components/MessageInput'
import AnalysisResult from '@/components/AnalysisResult'
import HistorySidebar from '@/components/HistorySidebar'
import { processMessage, getHistory, PipelineResult, ComparisonResult } from '@/lib/api'

const SAMPLES = [
  { label: 'A', title: 'Angry Customer', text: 'i ordered the premium plan 3 weeks ago and STILL havent received any confirmation email or access. this is absolutely ridiculous. i paid Rs 4999 and nobody has responded to my 4 emails. if this isnt fixed today im disputing the charge with my bank. my name is Rohan Mehta and my order id is ORD-8821.' },
  { label: 'B', title: 'Confused Query', text: 'hi I saw your AI tool on linkedin and I am curious how it works for small businesses? like do you guys offer any free trial or something? also can it work with whatsapp? just exploring options for now nothing urgent.' },
  { label: 'C', title: 'Positive Feedback', text: 'Just wanted to say the onboarding session last Tuesday was really well done. Priya from your team was super helpful and patient. The tool is working great so far. Looking forward to the advanced features you mentioned. Keep it up!' }
]

export default function Dashboard() {
  const [history, setHistory] = useState<(PipelineResult | ComparisonResult)[]>([])
  const [currentResult, setCurrentResult] = useState<PipelineResult | ComparisonResult | null>(null)
  const [isLoading, setIsLoading] = useState(false)
  const [messageKey, setMessageKey] = useState(0) // Used to force re-render/prefill

  useEffect(() => {
    fetchHistory()
  }, [])

  const fetchHistory = async () => {
    try {
      const data = await getHistory()
      setHistory(data)
    } catch (err) {
      console.error(err)
    }
  }

  const handleProcess = async (message: string, model: string) => {
    setIsLoading(true)
    try {
      const result = await processMessage(message, model)
      setCurrentResult(result)
      await fetchHistory()
    } catch (err) {
      console.error(err)
    } finally {
      setIsLoading(false)
    }
  }

  return (
    <div className="flex h-[calc(100vh-64px)] overflow-hidden">
      {/* Sidebar */}
      <HistorySidebar 
        history={history} 
        onSelect={setCurrentResult} 
        onClear={() => setHistory([])} 
      />

      {/* Main Content */}
      <div className="flex-1 overflow-y-auto bg-background transition-colors duration-300 custom-scrollbar">
        <div className="mx-auto max-w-6xl px-8 py-12 space-y-12">
          
          {/* Header */}
          <div className="space-y-2">
            <div className="flex items-center gap-2 text-blue-500">
              <Sparkles className="h-5 w-5" />
              <span className="text-xs font-bold uppercase tracking-[0.2em]">Next-Gen Support Pipeline</span>
            </div>
            <h1 className="text-4xl font-extrabold tracking-tight text-foreground sm:text-5xl">
              Understand customers, <span className="text-blue-500 underline decoration-blue-500/30 underline-offset-8">instantly.</span>
            </h1>
            <p className="text-muted-foreground max-w-xl leading-relaxed">
              Transform messy messages into structured insights and empathetic replies using multi-model reasoning.
            </p>
          </div>

          {/* Quick Samples */}
          <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
            {SAMPLES.map((s) => (
              <button
                key={s.label}
                onClick={() => handleProcess(s.text, 'claude')}
                className="group relative flex flex-col gap-2 rounded-2xl border border-border bg-card/50 p-4 text-left transition-all hover:bg-card/80 hover:border-blue-500/30 active:scale-[0.98]"
              >
                <div className="flex items-center justify-between">
                  <span className="text-[10px] font-bold uppercase tracking-widest text-muted-foreground">Sample {s.label}</span>
                  <ArrowRight className="h-3 w-3 text-muted-foreground transition-transform group-hover:translate-x-1 group-hover:text-blue-500" />
                </div>
                <span className="text-sm font-bold text-foreground">{s.title}</span>
              </button>
            ))}
          </div>

          <MessageInput onProcess={handleProcess} isLoading={isLoading} />

          <AnimatePresence mode="wait">
            {currentResult && (
              <motion.div
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                exit={{ opacity: 0, y: -20 }}
                className="space-y-8"
              >
                <div className="flex items-center gap-3 py-4">
                    <LayoutPanelLeft className="h-5 w-5 text-muted-foreground" />
                    <h2 className="text-xl font-bold text-foreground">Analysis Results</h2>
                </div>

                {'claude' in currentResult || 'gemini' in currentResult || 'openai' in currentResult ? (
                  <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
                    {(currentResult as ComparisonResult).claude && <AnalysisResult result={(currentResult as ComparisonResult).claude!} title="Claude Core" />}
                    {(currentResult as ComparisonResult).openai && <AnalysisResult result={(currentResult as ComparisonResult).openai!} title="OpenAI Mini" />}
                    {(currentResult as ComparisonResult).gemini && <AnalysisResult result={(currentResult as ComparisonResult).gemini!} title="Gemini Flash" />}
                  </div>
                ) : (
                  <AnalysisResult result={currentResult as PipelineResult} />
                )}
              </motion.div>
            )}
          </AnimatePresence>
        </div>
      </div>
    </div>
  )
}

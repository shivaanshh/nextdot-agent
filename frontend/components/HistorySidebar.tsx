'use client'

import React from 'react'
import { History, MessageSquare, Clock, Trash2 } from 'lucide-react'
import { cn } from '@/lib/utils'
import { PipelineResult, ComparisonResult } from '@/lib/api'

interface HistorySidebarProps {
  history: (PipelineResult | ComparisonResult)[]
  onSelect: (item: PipelineResult | ComparisonResult) => void
  onClear: () => void
}

export default function HistorySidebar({ history, onSelect, onClear }: HistorySidebarProps) {
  return (
    <div className="flex flex-col h-full border-r border-border bg-card/80 backdrop-blur-xl w-80 transition-colors duration-300">
      <div className="p-6 border-b border-border flex items-center justify-between">
        <div className="flex items-center gap-2">
          <History className="h-4 w-4 text-muted-foreground" />
          <h2 className="text-sm font-bold uppercase tracking-widest text-foreground">History</h2>
        </div>
        {history.length > 0 && (
          <button 
            onClick={onClear}
            className="text-muted-foreground hover:text-destructive p-1 rounded-md transition-colors"
          >
            <Trash2 className="h-4 w-4" />
          </button>
        )}
      </div>
      
      <div className="flex-1 overflow-y-auto custom-scrollbar">
        {history.length === 0 ? (
          <div className="flex flex-col items-center justify-center h-full p-8 text-center text-muted-foreground">
            <Clock className="h-8 w-8 mb-2 opacity-20" />
            <p className="text-xs uppercase tracking-widest font-bold opacity-40">No history yet</p>
          </div>
        ) : (
          <div className="p-4 space-y-2">
            {history.map((item, idx) => {
              // Handle both single and comparison results
              const displayItem = 'input_message' in item ? item : (item.claude || item.openai || item.gemini)
              if (!displayItem) return null

              return (
                <button
                  key={idx}
                  onClick={() => onSelect(item)}
                  className="w-full text-left p-4 rounded-xl border border-border bg-secondary/50 hover:bg-secondary transition-all group"
                >
                  <div className="flex items-start gap-3">
                    <MessageSquare className="h-4 w-4 text-blue-500 mt-1 flex-shrink-0" />
                    <div className="overflow-hidden">
                      <p className="text-xs text-foreground line-clamp-2 leading-relaxed font-medium">
                        {displayItem.input_message}
                      </p>
                      <div className="mt-2 flex items-center gap-2 text-[10px] text-muted-foreground font-bold uppercase tracking-tighter">
                        <span>{displayItem.classification?.intent || '—'}</span>
                        <span className="w-1 h-1 rounded-full bg-border" />
                        <span>{displayItem.timestamp ? new Date(displayItem.timestamp).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }) : '—'}</span>
                      </div>
                    </div>
                  </div>
                </button>
              )
            })}
          </div>
        )}
      </div>

      <div className="p-6 text-[10px] text-muted-foreground font-bold uppercase tracking-widest border-t border-border text-center">
        Powered by Nextdot AI
      </div>
    </div>
  )
}

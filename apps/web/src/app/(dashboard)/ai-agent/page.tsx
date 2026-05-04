'use client'

import { useState, useRef, useEffect } from 'react'
import { TopBar } from '@/components/layout/TopBar'
import { AiConfidenceBar } from '@/components/ai/AiConfidenceBar'
import { apiClient } from '@/lib/api/client'

type AgentType = 'general' | 'quality' | 'haccp' | 'equipment'

interface Message {
  role: 'user' | 'agent'
  content: string
  confidence?: number
}

const AGENT_LABELS: Record<AgentType, string> = {
  general: '일반',
  quality: '품질분석',
  haccp: 'HACCP',
  equipment: '설비진단',
}

export default function AiAgentPage() {
  const [messages, setMessages] = useState<Message[]>([])
  const [selectedAgent, setSelectedAgent] = useState<AgentType>('general')
  const [input, setInput] = useState('')
  const [loading, setLoading] = useState(false)
  const messagesEndRef = useRef<HTMLDivElement>(null)

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [messages])

  const handleSubmit = async () => {
    const trimmed = input.trim()
    if (!trimmed || loading) return

    setMessages((prev) => [...prev, { role: 'user', content: trimmed }])
    setInput('')
    setLoading(true)

    try {
      const { data } = await apiClient.post('/api/v1/ai/chat', {
        message: trimmed,
        agent_type: selectedAgent,
        context: {},
      })
      setMessages((prev) => [
        ...prev,
        { role: 'agent', content: data.reply, confidence: data.confidence },
      ])
    } catch (err) {
      setMessages((prev) => [
        ...prev,
        { role: 'agent', content: '응답 처리 중 오류가 발생했습니다. 다시 시도해 주세요.', confidence: 0 },
      ])
    } finally {
      setLoading(false)
    }
  }

  const handleKeyDown = (e: React.KeyboardEvent<HTMLInputElement>) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault()
      handleSubmit()
    }
  }

  return (
    <div className="flex flex-col min-h-full">
      <TopBar title="AI Agent Hub" />
      <div className="flex flex-1 overflow-hidden" style={{ height: 'calc(100vh - 57px)' }}>
        {/* Left panel — agent selector */}
        <div className="w-1/3 border-r bg-card p-4 flex flex-col gap-2">
          <p className="text-xs font-semibold text-muted-foreground mb-2">에이전트 유형 선택</p>
          {(Object.keys(AGENT_LABELS) as AgentType[]).map((agent) => (
            <button
              key={agent}
              onClick={() => setSelectedAgent(agent)}
              className={`w-full text-left px-4 py-3 rounded-lg text-sm font-medium transition-colors ${
                selectedAgent === agent
                  ? 'bg-primary text-primary-foreground'
                  : 'border border-border hover:bg-muted/40'
              }`}
            >
              {AGENT_LABELS[agent]}
            </button>
          ))}
          <div className="mt-auto pt-4 border-t">
            <p className="text-xs text-muted-foreground">
              현재 에이전트:{' '}
              <span className="font-semibold text-foreground">{AGENT_LABELS[selectedAgent]}</span>
            </p>
          </div>
        </div>

        {/* Right panel — chat */}
        <div className="flex-1 flex flex-col">
          <div className="flex-1 overflow-y-auto p-4 space-y-4">
            {messages.length === 0 && (
              <div className="flex items-center justify-center h-full">
                <p className="text-sm text-muted-foreground">
                  질문을 입력하여 AI 에이전트와 대화를 시작하세요
                </p>
              </div>
            )}
            {messages.map((msg, i) => (
              <div key={i} className={`flex ${msg.role === 'user' ? 'justify-end' : 'justify-start'}`}>
                <div
                  className={`max-w-[75%] rounded-lg px-4 py-3 space-y-1.5 ${
                    msg.role === 'user'
                      ? 'bg-primary text-primary-foreground'
                      : 'bg-card border border-border'
                  }`}
                >
                  <p className="text-sm whitespace-pre-wrap">{msg.content}</p>
                  {msg.role === 'agent' && msg.confidence !== undefined && (
                    <AiConfidenceBar
                      confidence={msg.confidence}
                      modelName="rule-based"
                      className="mt-1"
                    />
                  )}
                </div>
              </div>
            ))}
            {loading && (
              <div className="flex justify-start">
                <div className="bg-card border border-border rounded-lg px-4 py-3">
                  <div className="flex items-center gap-2">
                    <div className="w-2 h-2 rounded-full bg-muted-foreground animate-bounce" style={{ animationDelay: '0ms' }} />
                    <div className="w-2 h-2 rounded-full bg-muted-foreground animate-bounce" style={{ animationDelay: '150ms' }} />
                    <div className="w-2 h-2 rounded-full bg-muted-foreground animate-bounce" style={{ animationDelay: '300ms' }} />
                  </div>
                </div>
              </div>
            )}
            <div ref={messagesEndRef} />
          </div>

          <div className="border-t p-4 flex gap-2">
            <input
              type="text"
              value={input}
              onChange={(e) => setInput(e.target.value)}
              onKeyDown={handleKeyDown}
              placeholder={`${AGENT_LABELS[selectedAgent]} 에이전트에게 질문하기...`}
              disabled={loading}
              className="flex-1 rounded-lg border border-border bg-background px-4 py-2 text-sm outline-none focus:ring-2 focus:ring-primary/30 disabled:opacity-50"
            />
            <button
              onClick={handleSubmit}
              disabled={loading || !input.trim()}
              className="px-4 py-2 rounded-lg bg-primary text-primary-foreground text-sm font-medium hover:bg-primary/90 disabled:opacity-50 transition-colors"
            >
              전송
            </button>
          </div>
        </div>
      </div>
    </div>
  )
}

import { useState, useEffect, useRef } from 'react'
import { MessageSquare, Send, Loader2, Bot, User, Trash2, AlertCircle, HelpCircle } from 'lucide-react'
import MainLayout from '../layouts/MainLayout'
import { listContracts, sendChatMessage, getChatHistory, clearChatHistory } from '../services/api'
import { format, parseISO } from 'date-fns'
import clsx from 'clsx'

const SUGGESTED_QUESTIONS = [
  'What are the biggest risks in this contract?',
  'Is there an auto-renewal clause?',
  'What is the liability cap?',
  'What are the payment terms?',
  'How can I terminate this contract?',
  'Is there a data protection clause?',
  'What does the confidentiality clause say?',
  'Who are the parties in this contract?',
]

function MessageBubble({ msg }) {
  const isUser = msg.role === 'user'
  const formatContent = (content) => {
    // Convert markdown-like formatting to HTML
    return content
      .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
      .replace(/\*(.*?)\*/g, '<em>$1</em>')
      .replace(/`(.*?)`/g, '<code class="font-mono text-indigo-300 bg-slate-800 px-1 rounded">$1</code>')
      .split('\n')
      .map(line => {
        if (line.startsWith('- ') || line.startsWith('• ')) {
          return `<li class="ml-4">${line.slice(2)}</li>`
        }
        return `<p>${line || '&nbsp;'}</p>`
      })
      .join('')
  }

  return (
    <div className={clsx('flex gap-3 mb-4', isUser ? 'justify-end' : 'justify-start')}>
      {!isUser && (
        <div className="w-7 h-7 rounded-lg bg-indigo-600/30 border border-indigo-500/40 flex items-center justify-center flex-shrink-0 mt-0.5">
          <Bot className="w-3.5 h-3.5 text-indigo-400" />
        </div>
      )}
      <div className={clsx(
        'max-w-[80%] rounded-xl px-4 py-3 text-sm leading-relaxed',
        isUser
          ? 'bg-indigo-600/30 border border-indigo-500/30 text-slate-100 rounded-tr-sm'
          : 'bg-slate-800/80 border border-slate-700/60 text-slate-300 rounded-tl-sm'
      )}>
        {isUser ? (
          <p>{msg.content}</p>
        ) : (
          <div
            className="prose-dark space-y-1"
            dangerouslySetInnerHTML={{ __html: formatContent(msg.content) }}
          />
        )}
        <p className="text-[10px] text-slate-600 mt-1.5">
          {msg.created_at ? format(parseISO(msg.created_at), 'h:mm a') : ''}
        </p>
      </div>
      {isUser && (
        <div className="w-7 h-7 rounded-lg bg-slate-700 flex items-center justify-center flex-shrink-0 mt-0.5">
          <User className="w-3.5 h-3.5 text-slate-400" />
        </div>
      )}
    </div>
  )
}

export default function Assistant() {
  const [contracts, setContracts] = useState([])
  const [selectedId, setSelectedId] = useState('')
  const [messages, setMessages] = useState([])
  const [input, setInput] = useState('')
  const [sending, setSending] = useState(false)
  const [error, setError] = useState('')
  const [loadingHistory, setLoadingHistory] = useState(false)
  const bottomRef = useRef(null)
  const inputRef = useRef(null)

  useEffect(() => {
    listContracts().then(r => {
      const analyzed = r.data.filter(c => c.status === 'analyzed')
      setContracts(analyzed)
    }).catch(() => {})
  }, [])

  useEffect(() => {
    if (selectedId) {
      setLoadingHistory(true)
      getChatHistory(selectedId)
        .then(r => setMessages(r.data))
        .catch(() => setMessages([]))
        .finally(() => setLoadingHistory(false))
    } else {
      setMessages([])
    }
  }, [selectedId])

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [messages])

  const handleSend = async (text) => {
    const msg = (text || input).trim()
    if (!msg || !selectedId || sending) return
    setInput('')
    setError('')

    const userMsg = { id: Date.now(), role: 'user', content: msg, created_at: new Date().toISOString() }
    setMessages(prev => [...prev, userMsg])
    setSending(true)

    try {
      const res = await sendChatMessage(selectedId, msg)
      setMessages(prev => [...prev, res.data])
    } catch (e) {
      setError(e.message)
      setMessages(prev => prev.filter(m => m.id !== userMsg.id))
    } finally {
      setSending(false)
      inputRef.current?.focus()
    }
  }

  const handleClear = async () => {
    if (!selectedId) return
    if (!window.confirm('Clear chat history for this contract?')) return
    try {
      await clearChatHistory(selectedId)
      setMessages([])
    } catch (e) {
      setError(e.message)
    }
  }

  const selectedContract = contracts.find(c => c.id === Number(selectedId))

  return (
    <MainLayout title="AI Contract Assistant" subtitle="Ask questions about your contracts">
      <div className="flex flex-col h-[calc(100vh-8rem)] animate-slide-up">
        {/* Contract Selector Bar */}
        <div className="glass-card p-3 mb-4 flex items-center gap-4">
          <div className="flex-1 flex items-center gap-3">
            <MessageSquare className="w-4 h-4 text-indigo-400 flex-shrink-0" />
            <select
              value={selectedId}
              onChange={e => setSelectedId(e.target.value)}
              className="input-field max-w-sm"
            >
              <option value="">Select a contract to chat about...</option>
              {contracts.map(c => (
                <option key={c.id} value={c.id}>{c.original_name}</option>
              ))}
            </select>
            {selectedContract && (
              <span className="text-xs text-slate-500 hidden sm:block">
                Chat with AI about: <strong className="text-slate-400">{selectedContract.original_name}</strong>
              </span>
            )}
          </div>
          {selectedId && messages.length > 0 && (
            <button onClick={handleClear} className="btn-danger text-xs py-1.5 px-3">
              <Trash2 className="w-3 h-3" /> Clear
            </button>
          )}
        </div>

        {!selectedId ? (
          <div className="flex-1 glass-card flex flex-col items-center justify-center gap-4 text-center p-8">
            <div className="w-16 h-16 rounded-2xl bg-indigo-600/10 border border-indigo-500/20 flex items-center justify-center">
              <MessageSquare className="w-8 h-8 text-indigo-400" />
            </div>
            <div>
              <h3 className="text-lg font-semibold text-slate-200">Select a contract to start chatting</h3>
              <p className="text-slate-500 text-sm mt-1">The AI assistant answers questions about your analyzed contracts</p>
            </div>
            {contracts.length === 0 && (
              <p className="text-xs text-amber-400/70 flex items-center gap-1.5">
                <AlertCircle className="w-3.5 h-3.5" />
                No analyzed contracts found. Upload and analyze a contract first.
              </p>
            )}
          </div>
        ) : (
          <div className="flex-1 flex flex-col glass-card overflow-hidden min-h-0">
            {/* Messages */}
            <div className="flex-1 overflow-y-auto p-5">
              {loadingHistory ? (
                <div className="flex items-center justify-center py-8">
                  <Loader2 className="w-5 h-5 text-indigo-400 animate-spin" />
                </div>
              ) : messages.length === 0 ? (
                <div className="flex flex-col items-center gap-5 py-6">
                  <div className="w-12 h-12 rounded-xl bg-indigo-600/20 border border-indigo-500/30 flex items-center justify-center">
                    <Bot className="w-6 h-6 text-indigo-400" />
                  </div>
                  <div className="text-center">
                    <h4 className="text-sm font-semibold text-slate-300">Lexora AI Assistant</h4>
                    <p className="text-xs text-slate-500 mt-1">Ask me anything about this contract</p>
                  </div>
                  <div>
                    <p className="section-label text-center mb-3">Suggested Questions</p>
                    <div className="grid grid-cols-1 sm:grid-cols-2 gap-2 max-w-lg">
                      {SUGGESTED_QUESTIONS.map((q, i) => (
                        <button
                          key={i}
                          onClick={() => handleSend(q)}
                          className="text-left text-xs text-slate-400 hover:text-indigo-300 px-3 py-2 rounded-lg bg-slate-800/60 border border-slate-700/60 hover:border-indigo-500/40 hover:bg-indigo-600/10 transition-all duration-150"
                        >
                          <HelpCircle className="w-3 h-3 inline mr-1.5 opacity-60" />
                          {q}
                        </button>
                      ))}
                    </div>
                  </div>
                </div>
              ) : (
                <>
                  {messages.map((msg, i) => (
                    <MessageBubble key={msg.id || i} msg={msg} />
                  ))}
                  {sending && (
                    <div className="flex gap-3 mb-4">
                      <div className="w-7 h-7 rounded-lg bg-indigo-600/30 border border-indigo-500/40 flex items-center justify-center flex-shrink-0">
                        <Bot className="w-3.5 h-3.5 text-indigo-400" />
                      </div>
                      <div className="px-4 py-3 rounded-xl rounded-tl-sm bg-slate-800/80 border border-slate-700/60">
                        <div className="flex gap-1 items-center h-4">
                          {[0, 1, 2].map(i => (
                            <span
                              key={i}
                              className="w-1.5 h-1.5 bg-slate-500 rounded-full animate-bounce"
                              style={{ animationDelay: `${i * 0.15}s` }}
                            />
                          ))}
                        </div>
                      </div>
                    </div>
                  )}
                  <div ref={bottomRef} />
                </>
              )}
            </div>

            {/* Error */}
            {error && (
              <div className="px-4 py-2 bg-red-500/10 border-t border-red-500/20 text-red-400 text-xs flex items-center gap-2">
                <AlertCircle className="w-3 h-3" /> {error}
              </div>
            )}

            {/* Input */}
            <div className="p-4 border-t border-slate-800/60">
              <div className="flex gap-3">
                <input
                  ref={inputRef}
                  type="text"
                  value={input}
                  onChange={e => setInput(e.target.value)}
                  onKeyDown={e => e.key === 'Enter' && !e.shiftKey && handleSend()}
                  placeholder="Ask about this contract..."
                  className="input-field flex-1"
                  disabled={sending}
                />
                <button
                  onClick={() => handleSend()}
                  disabled={!input.trim() || sending}
                  className="btn-primary px-4 disabled:opacity-40"
                >
                  {sending
                    ? <Loader2 className="w-4 h-4 animate-spin" />
                    : <Send className="w-4 h-4" />
                  }
                </button>
              </div>
              <p className="text-[10px] text-slate-700 mt-1.5">Press Enter to send • Answers are based on contract content</p>
            </div>
          </div>
        )}
      </div>
    </MainLayout>
  )
}

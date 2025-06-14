'use client'

import { useState, useRef, useEffect } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import { 
  ArrowLeftIcon,
  PaperAirplaneIcon,
  SparklesIcon,
  UserIcon,
  ChatBubbleLeftIcon
} from '@heroicons/react/24/outline'
import { toast } from 'react-hot-toast'
import { AnalysisResult } from '@/types/analysis'
import { useChat } from '@/hooks/useChat'
import ChatMessage from './ChatMessage'
import ChatSuggestions from './ChatSuggestions'

interface ChatInterfaceProps {
  analysisResult: AnalysisResult
  onBackToResults: () => void
}

export default function ChatInterface({
  analysisResult,
  onBackToResults,
}: ChatInterfaceProps) {
  const [message, setMessage] = useState('')
  const [isTyping, setIsTyping] = useState(false)
  const messagesEndRef = useRef<HTMLDivElement>(null)
  const inputRef = useRef<HTMLInputElement>(null)

  const {
    messages,
    sendMessage,
    isLoading,
    sessionId,
    createSession,
    suggestions,
  } = useChat()

  // Initialize chat session with analysis context
  useEffect(() => {
    if (analysisResult.id) {
      createSession({
        title: '分析結果について相談',
        analysisId: analysisResult.id,
        initialMessage: `こんにちは！先程の分析結果（総合スコア: ${analysisResult.overall_score.score}点）について相談したいです。`,
      })
    }
  }, [analysisResult.id, createSession])

  // Auto scroll to bottom
  useEffect(() => {
    scrollToBottom()
  }, [messages])

  // Focus input on mount
  useEffect(() => {
    if (inputRef.current) {
      inputRef.current.focus()
    }
  }, [])

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }

  const handleSendMessage = async () => {
    if (!message.trim() || isLoading || !sessionId) return

    const messageToSend = message.trim()
    setMessage('')
    setIsTyping(true)

    try {
      await sendMessage(sessionId, messageToSend, analysisResult.id)
    } catch (error) {
      toast.error('メッセージの送信に失敗しました')
    } finally {
      setIsTyping(false)
    }
  }

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault()
      handleSendMessage()
    }
  }

  const handleSuggestionClick = (suggestion: string) => {
    setMessage(suggestion)
    if (inputRef.current) {
      inputRef.current.focus()
    }
  }

  return (
    <div className="min-h-screen bg-gradient-soft">
      {/* Header */}
      <div className="bg-white/80 backdrop-blur-md border-b border-pink-100 sticky top-0 z-40">
        <div className="max-w-4xl mx-auto px-4 py-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center">
              <button
                onClick={onBackToResults}
                className="mr-4 p-2 hover:bg-gray-100 rounded-lg transition-colors duration-200"
              >
                <ArrowLeftIcon className="w-5 h-5 text-gray-600" />
              </button>
              
              <div className="flex items-center">
                <div className="w-10 h-10 bg-gradient-korean rounded-full flex items-center justify-center mr-3">
                  <SparklesIcon className="w-6 h-6 text-white" />
                </div>
                <div>
                  <h1 className="font-bold text-gray-900">
                    AI美容コンサルタント
                  </h1>
                  <p className="text-sm text-gray-600">
                    韓国美容のプロフェッショナル
                  </p>
                </div>
              </div>
            </div>

            <div className="text-sm text-gray-500">
              分析結果: {analysisResult.overall_score.score.toFixed(1)}点
            </div>
          </div>
        </div>
      </div>

      {/* Chat Messages */}
      <div className="max-w-4xl mx-auto px-4 py-6">
        <div className="bg-white rounded-2xl shadow-soft min-h-[600px] flex flex-col">
          
          {/* Welcome Message */}
          {messages.length === 0 && (
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.6 }}
              className="p-8 text-center border-b border-gray-100"
            >
              <div className="w-16 h-16 bg-gradient-korean rounded-full flex items-center justify-center mx-auto mb-4">
                <ChatBubbleLeftIcon className="w-8 h-8 text-white" />
              </div>
              <h2 className="text-xl font-bold text-gray-900 mb-2">
                美容相談へようこそ！
              </h2>
              <p className="text-gray-600 max-w-md mx-auto">
                あなたの分析結果をもとに、韓国美容のプロフェッショナルが
                パーソナライズされたアドバイスを提供します。
              </p>
            </motion.div>
          )}

          {/* Messages */}
          <div className="flex-1 p-6 space-y-4 overflow-y-auto max-h-[500px]">
            <AnimatePresence>
              {messages.map((msg, index) => (
                <ChatMessage
                  key={msg.id || index}
                  message={msg}
                  isLast={index === messages.length - 1}
                />
              ))}
            </AnimatePresence>

            {/* Typing Indicator */}
            {(isLoading || isTyping) && (
              <motion.div
                initial={{ opacity: 0, scale: 0.9 }}
                animate={{ opacity: 1, scale: 1 }}
                exit={{ opacity: 0, scale: 0.9 }}
                className="flex items-center space-x-2"
              >
                <div className="w-8 h-8 bg-pink-100 rounded-full flex items-center justify-center">
                  <SparklesIcon className="w-4 h-4 text-pink-500" />
                </div>
                <div className="bg-gray-100 rounded-2xl px-4 py-3">
                  <div className="flex space-x-1">
                    <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" />
                    <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{ animationDelay: '0.1s' }} />
                    <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{ animationDelay: '0.2s' }} />
                  </div>
                </div>
              </motion.div>
            )}

            <div ref={messagesEndRef} />
          </div>

          {/* Suggestions */}
          {suggestions.length > 0 && (
            <div className="px-6 pb-4">
              <ChatSuggestions
                suggestions={suggestions}
                onSuggestionClick={handleSuggestionClick}
              />
            </div>
          )}

          {/* Input */}
          <div className="p-6 border-t border-gray-100">
            <div className="flex items-end space-x-4">
              <div className="flex-1">
                <div className="relative">
                  <input
                    ref={inputRef}
                    type="text"
                    value={message}
                    onChange={(e) => setMessage(e.target.value)}
                    onKeyPress={handleKeyPress}
                    placeholder="美容について何でもお聞きください..."
                    className="chat-input pr-12"
                    disabled={isLoading}
                  />
                  <button
                    onClick={handleSendMessage}
                    disabled={!message.trim() || isLoading}
                    className="absolute right-2 top-1/2 transform -translate-y-1/2 p-2 text-pink-500 hover:text-pink-600 disabled:text-gray-300 disabled:cursor-not-allowed transition-colors duration-200"
                  >
                    <PaperAirplaneIcon className="w-5 h-5" />
                  </button>
                </div>
              </div>
            </div>

            <div className="mt-2 text-xs text-gray-500 text-center">
              Shift + Enter で改行、Enter で送信
            </div>
          </div>
        </div>

        {/* Tips */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.6, delay: 0.4 }}
          className="mt-6 bg-blue-50 border border-blue-200 rounded-xl p-4"
        >
          <h3 className="font-semibold text-blue-900 mb-2">
            💡 相談のコツ
          </h3>
          <ul className="text-sm text-blue-800 space-y-1">
            <li>• 具体的な悩みや気になる部分について質問してください</li>
            <li>• 予算や時間の制約があれば教えてください</li>
            <li>• 韓国コスメやK-Beautyについても詳しくご案内できます</li>
            <li>• メイク方法やスキンケアルーティンもお任せください</li>
          </ul>
        </motion.div>
      </div>
    </div>
  )
}
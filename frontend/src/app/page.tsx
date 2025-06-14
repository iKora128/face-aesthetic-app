'use client'

import { useState } from 'react'
import { motion } from 'framer-motion'
import Header from '@/components/layout/Header'
import Hero from '@/components/sections/Hero'
import AnalysisUpload from '@/components/analysis/AnalysisUpload'
import AnalysisResults from '@/components/analysis/AnalysisResults'
import ChatInterface from '@/components/chat/ChatInterface'
import Footer from '@/components/layout/Footer'
import { AnalysisResult } from '@/types/analysis'

export default function HomePage() {
  const [currentStep, setCurrentStep] = useState<'upload' | 'results' | 'chat'>('upload')
  const [analysisResult, setAnalysisResult] = useState<AnalysisResult | null>(null)
  const [isLoading, setIsLoading] = useState(false)

  const handleAnalysisComplete = (result: AnalysisResult) => {
    setAnalysisResult(result)
    setCurrentStep('results')
  }

  const handleStartChat = () => {
    setCurrentStep('chat')
  }

  const handleBackToUpload = () => {
    setCurrentStep('upload')
    setAnalysisResult(null)
  }

  return (
    <div className="min-h-screen">
      <Header />
      
      <main className="relative">
        {currentStep === 'upload' && (
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            transition={{ duration: 0.6 }}
          >
            {/* Hero Section */}
            <Hero />
            
            {/* Analysis Upload Section */}
            <section className="py-20 px-4">
              <div className="max-w-4xl mx-auto">
                <motion.div
                  initial={{ opacity: 0, y: 40 }}
                  animate={{ opacity: 1, y: 0 }}
                  transition={{ duration: 0.8, delay: 0.2 }}
                  className="text-center mb-12"
                >
                  <h2 className="text-3xl sm:text-4xl font-bold text-gray-900 mb-4">
                    顔面美容分析を
                    <span className="text-gradient"> 始めましょう</span>
                  </h2>
                  <p className="text-lg text-gray-600 max-w-2xl mx-auto">
                    最新のAI技術で、あなたの美しさを科学的に分析。
                    韓国美容のプロフェッショナルがサポートします。
                  </p>
                </motion.div>

                <AnalysisUpload
                  onAnalysisComplete={handleAnalysisComplete}
                  isLoading={isLoading}
                  setIsLoading={setIsLoading}
                />
              </div>
            </section>
          </motion.div>
        )}

        {currentStep === 'results' && analysisResult && (
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            transition={{ duration: 0.6 }}
          >
            <AnalysisResults
              result={analysisResult}
              onStartChat={handleStartChat}
              onBackToUpload={handleBackToUpload}
            />
          </motion.div>
        )}

        {currentStep === 'chat' && analysisResult && (
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            transition={{ duration: 0.6 }}
          >
            <ChatInterface
              analysisResult={analysisResult}
              onBackToResults={() => setCurrentStep('results')}
            />
          </motion.div>
        )}

        {/* Features Section (visible only on upload step) */}
        {currentStep === 'upload' && (
          <section className="py-20 bg-gradient-soft">
            <div className="max-w-6xl mx-auto px-4">
              <motion.div
                initial={{ opacity: 0, y: 40 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ duration: 0.8, delay: 0.4 }}
                className="text-center mb-16"
              >
                <h2 className="text-3xl sm:text-4xl font-bold text-gray-900 mb-4">
                  なぜFace Aesthetic AIが
                  <span className="text-gradient"> 選ばれるのか</span>
                </h2>
                <p className="text-lg text-gray-600 max-w-3xl mx-auto">
                  最先端のAI技術と韓国美容の専門知識を組み合わせた、
                  革新的な美容分析プラットフォームです。
                </p>
              </motion.div>

              <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
                {features.map((feature, index) => (
                  <motion.div
                    key={feature.title}
                    initial={{ opacity: 0, y: 40 }}
                    animate={{ opacity: 1, y: 0 }}
                    transition={{ duration: 0.6, delay: 0.1 * index }}
                    className="korean-card p-8 text-center hover:shadow-beauty transition-all duration-300"
                  >
                    <div className="w-16 h-16 bg-gradient-korean rounded-2xl flex items-center justify-center mx-auto mb-6">
                      <span className="text-2xl">{feature.icon}</span>
                    </div>
                    <h3 className="text-xl font-bold text-gray-900 mb-4">
                      {feature.title}
                    </h3>
                    <p className="text-gray-600 leading-relaxed">
                      {feature.description}
                    </p>
                  </motion.div>
                ))}
              </div>
            </div>
          </section>
        )}
      </main>

      <Footer />
    </div>
  )
}

const features = [
  {
    icon: '🎯',
    title: '高精度AI分析',
    description: 'MediaPipeを使用した468点の顔面ランドマーク検出により、ミリメートル単位での正確な分析を実現'
  },
  {
    icon: '🇰🇷',
    title: 'K-Beauty基準',
    description: '韓国美容業界の最新トレンドと黄金比理論に基づいた、科学的な美容評価システム'
  },
  {
    icon: '💬',
    title: 'AI美容コンサル',
    description: 'ChatGPT-4o-miniを搭載した韓国美容のプロによる、個別化されたアドバイスとカウンセリング'
  },
  {
    icon: '📊',
    title: '詳細レポート',
    description: 'Eライン、対称性、パーツ調和など多角的な分析結果を美しいビジュアルレポートで提供'
  },
  {
    icon: '🔒',
    title: 'プライバシー保護',
    description: 'Supabaseによる堅牢なセキュリティと、GDPR準拠のデータ保護で安心してご利用いただけます'
  },
  {
    icon: '✨',
    title: '継続的改善',
    description: '定期的なAIモデルの更新と新機能追加により、常に最高の分析体験を提供'
  }
]
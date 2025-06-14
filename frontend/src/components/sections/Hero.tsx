'use client'

import { motion } from 'framer-motion'
import { 
  SparklesIcon, 
  ChartBarIcon, 
  ChatBubbleLeftRightIcon,
  ShieldCheckIcon 
} from '@heroicons/react/24/outline'

export default function Hero() {
  return (
    <section className="relative py-20 sm:py-32 overflow-hidden" id="home">
      {/* Background Elements */}
      <div className="absolute inset-0">
        <div className="absolute top-20 left-10 w-32 h-32 bg-pink-200 rounded-full opacity-20 animate-float" />
        <div className="absolute top-40 right-20 w-24 h-24 bg-purple-200 rounded-full opacity-20 animate-float" style={{ animationDelay: '1s' }} />
        <div className="absolute bottom-20 left-1/4 w-20 h-20 bg-sky-200 rounded-full opacity-20 animate-float" style={{ animationDelay: '2s' }} />
      </div>

      <div className="relative max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="text-center">
          {/* Hero Headline */}
          <motion.div
            initial={{ opacity: 0, y: 40 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.8 }}
            className="mb-8"
          >
            <h1 className="text-4xl sm:text-5xl lg:text-6xl font-bold text-gray-900 mb-6">
              <span className="block">AI が導く</span>
              <span className="text-gradient block">美しさの新次元</span>
            </h1>
            <p className="text-xl sm:text-2xl text-gray-600 max-w-3xl mx-auto leading-relaxed">
              最先端のAI技術と韓国美容の専門知識で、
              <br className="hidden sm:block" />
              あなたの美しさを科学的に分析・向上させます
            </p>
          </motion.div>

          {/* CTA Buttons */}
          <motion.div
            initial={{ opacity: 0, y: 40 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.8, delay: 0.2 }}
            className="flex flex-col sm:flex-row items-center justify-center gap-4 mb-16"
          >
            <button className="korean-button w-full sm:w-auto">
              <SparklesIcon className="w-5 h-5 mr-2" />
              無料で分析を始める
            </button>
            <button className="btn-outline w-full sm:w-auto">
              デモを見る
            </button>
          </motion.div>

          {/* Stats */}
          <motion.div
            initial={{ opacity: 0, y: 40 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.8, delay: 0.4 }}
            className="grid grid-cols-2 lg:grid-cols-4 gap-8 mb-20"
          >
            {stats.map((stat, index) => (
              <div key={stat.label} className="text-center">
                <div className="text-3xl sm:text-4xl font-bold text-gradient mb-2">
                  {stat.value}
                </div>
                <div className="text-sm sm:text-base text-gray-600">
                  {stat.label}
                </div>
              </div>
            ))}
          </motion.div>

          {/* Features Grid */}
          <motion.div
            initial={{ opacity: 0, y: 40 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.8, delay: 0.6 }}
            className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-6"
          >
            {heroFeatures.map((feature, index) => (
              <motion.div
                key={feature.title}
                initial={{ opacity: 0, scale: 0.9 }}
                animate={{ opacity: 1, scale: 1 }}
                transition={{ duration: 0.6, delay: 0.1 * index }}
                className="korean-card p-6 text-center hover:shadow-beauty transition-all duration-300 group"
              >
                <div className="w-12 h-12 bg-gradient-korean rounded-xl flex items-center justify-center mx-auto mb-4 group-hover:scale-110 transition-transform duration-300">
                  <feature.icon className="w-6 h-6 text-white" />
                </div>
                <h3 className="font-semibold text-gray-900 mb-2">
                  {feature.title}
                </h3>
                <p className="text-sm text-gray-600">
                  {feature.description}
                </p>
              </motion.div>
            ))}
          </motion.div>
        </div>
      </div>
    </section>
  )
}

const stats = [
  { value: '468点', label: '顔面ランドマーク' },
  { value: '99.9%', label: '分析精度' },
  { value: '10万+', label: '利用ユーザー' },
  { value: '24/7', label: 'AIサポート' },
]

const heroFeatures = [
  {
    icon: SparklesIcon,
    title: '高精度AI分析',
    description: 'MediaPipe技術による正確な分析'
  },
  {
    icon: ChartBarIcon,
    title: '詳細レポート',
    description: '美しいビジュアルでの結果表示'
  },
  {
    icon: ChatBubbleLeftRightIcon,
    title: 'AI美容コンサル',
    description: '専門的なアドバイスとサポート'
  },
  {
    icon: ShieldCheckIcon,
    title: 'プライバシー保護',
    description: '安全なデータ管理と保護'
  }
]
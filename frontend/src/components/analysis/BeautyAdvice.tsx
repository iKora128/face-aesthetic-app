'use client'

import { motion } from 'framer-motion'
import { 
  SparklesIcon,
  LightBulbIcon,
  HeartIcon 
} from '@heroicons/react/24/outline'

interface BeautyAdviceProps {
  advice: string[]
}

export default function BeautyAdvice({ advice }: BeautyAdviceProps) {
  // Filter and clean advice
  const cleanedAdvice = advice
    .filter(item => item && item.trim().length > 0)
    .map(item => item.replace(/[⚠️✅💋✨🌟]/g, '').trim())
    .slice(0, 6) // Show max 6 pieces of advice

  const categories = [
    {
      title: 'スキンケア',
      icon: SparklesIcon,
      color: 'pink',
      items: cleanedAdvice.filter(item => 
        item.includes('スキンケア') || 
        item.includes('保湿') || 
        item.includes('肌')
      ).slice(0, 2)
    },
    {
      title: 'メイクアップ',
      icon: LightBulbIcon,
      color: 'purple',
      items: cleanedAdvice.filter(item => 
        item.includes('メイク') || 
        item.includes('化粧') || 
        item.includes('コンシーラー') ||
        item.includes('ハイライト')
      ).slice(0, 2)
    },
    {
      title: 'ライフスタイル',
      icon: HeartIcon,
      color: 'sky',
      items: cleanedAdvice.filter(item => 
        item.includes('運動') || 
        item.includes('睡眠') || 
        item.includes('食事') ||
        item.includes('マッサージ')
      ).slice(0, 2)
    }
  ]

  // If categorization doesn't capture all advice, add remaining to general
  const categorizedItems = categories.flatMap(cat => cat.items)
  const remainingAdvice = cleanedAdvice.filter(item => !categorizedItems.includes(item))

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.6 }}
      className="korean-card p-6 mb-8"
    >
      <div className="flex items-center mb-6">
        <SparklesIcon className="w-6 h-6 text-pink-500 mr-3" />
        <h3 className="text-xl font-bold text-gray-900">
          パーソナライズド美容アドバイス
        </h3>
      </div>

      {/* Categorized Advice */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-6">
        {categories.map((category, categoryIndex) => (
          category.items.length > 0 && (
            <motion.div
              key={category.title}
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.6, delay: 0.1 * categoryIndex }}
              className={`bg-${category.color}-50 border border-${category.color}-200 rounded-xl p-4`}
            >
              <div className="flex items-center mb-3">
                <category.icon className={`w-5 h-5 text-${category.color}-600 mr-2`} />
                <h4 className={`font-semibold text-${category.color}-900`}>
                  {category.title}
                </h4>
              </div>
              
              <div className="space-y-2">
                {category.items.map((item, index) => (
                  <motion.div
                    key={index}
                    initial={{ opacity: 0, x: -10 }}
                    animate={{ opacity: 1, x: 0 }}
                    transition={{ duration: 0.4, delay: 0.1 * index }}
                    className={`text-sm text-${category.color}-800 bg-white rounded-lg p-3 border border-${category.color}-100`}
                  >
                    {item}
                  </motion.div>
                ))}
              </div>
            </motion.div>
          )
        ))}
      </div>

      {/* Remaining Advice */}
      {remainingAdvice.length > 0 && (
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.6, delay: 0.4 }}
          className="bg-gradient-to-r from-pink-50 to-purple-50 rounded-xl p-4"
        >
          <h4 className="font-semibold text-gray-900 mb-3 flex items-center">
            <LightBulbIcon className="w-5 h-5 text-amber-500 mr-2" />
            その他のアドバイス
          </h4>
          
          <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
            {remainingAdvice.map((item, index) => (
              <motion.div
                key={index}
                initial={{ opacity: 0, scale: 0.95 }}
                animate={{ opacity: 1, scale: 1 }}
                transition={{ duration: 0.4, delay: 0.05 * index }}
                className="bg-white rounded-lg p-3 border border-pink-100 text-sm text-gray-700"
              >
                <div className="flex items-start">
                  <span className="w-2 h-2 bg-pink-400 rounded-full mt-2 mr-3 flex-shrink-0" />
                  {item}
                </div>
              </motion.div>
            ))}
          </div>
        </motion.div>
      )}

      {/* Call to Action */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.6, delay: 0.6 }}
        className="mt-6 bg-gradient-korean rounded-xl p-6 text-white text-center"
      >
        <h4 className="font-bold text-lg mb-2">
          さらに詳しいアドバイスが必要ですか？
        </h4>
        <p className="text-pink-100 mb-4">
          韓国美容のプロフェッショナルAIがあなた専用の美容プランを作成します
        </p>
        <button className="bg-white text-pink-600 font-semibold py-2 px-6 rounded-full hover:bg-pink-50 transition-colors duration-200">
          AI美容相談を始める
        </button>
      </motion.div>

      {/* Disclaimer */}
      <motion.div
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        transition={{ duration: 0.6, delay: 0.8 }}
        className="mt-4 text-xs text-gray-500 text-center"
      >
        ※ このアドバイスは美容参考情報であり、医学的アドバイスではありません。
        個人の体質や肌質に合わせて調整してください。
      </motion.div>
    </motion.div>
  )
}
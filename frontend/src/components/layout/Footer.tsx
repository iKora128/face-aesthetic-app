'use client'

import { motion } from 'framer-motion'
import { 
  HeartIcon,
  SparklesIcon,
  EnvelopeIcon,
  PhoneIcon,
  MapPinIcon 
} from '@heroicons/react/24/outline'

export default function Footer() {
  const currentYear = new Date().getFullYear()

  const footerLinks = {
    service: [
      { name: '顔面美容分析', href: '#analysis' },
      { name: 'AI美容相談', href: '#consultation' },
      { name: 'レポート生成', href: '#reports' },
      { name: 'LINE Bot', href: '#linebot' },
    ],
    support: [
      { name: 'よくある質問', href: '#faq' },
      { name: 'お問い合わせ', href: '#contact' },
      { name: '使い方ガイド', href: '#guide' },
      { name: 'API仕様', href: '#api' },
    ],
    company: [
      { name: '会社概要', href: '#about' },
      { name: 'プライバシーポリシー', href: '#privacy' },
      { name: '利用規約', href: '#terms' },
      { name: '特定商取引法', href: '#commerce' },
    ],
    social: [
      { name: 'Twitter', href: '#', icon: '🐦' },
      { name: 'Instagram', href: '#', icon: '📷' },
      { name: 'YouTube', href: '#', icon: '📺' },
      { name: 'TikTok', href: '#', icon: '🎵' },
    ],
  }

  return (
    <footer className="bg-gray-900 text-white">
      {/* Main Footer */}
      <div className="max-w-7xl mx-auto px-4 py-16">
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-5 gap-8">
          
          {/* Brand Section */}
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.6 }}
            className="lg:col-span-2"
          >
            <div className="flex items-center space-x-3 mb-6">
              <div className="w-10 h-10 bg-gradient-korean rounded-lg flex items-center justify-center">
                <SparklesIcon className="w-6 h-6 text-white" />
              </div>
              <div>
                <h3 className="text-xl font-bold">Face Aesthetic AI</h3>
                <p className="text-gray-400 text-sm">顔面美容分析プラットフォーム</p>
              </div>
            </div>
            
            <p className="text-gray-300 leading-relaxed mb-6 max-w-md">
              最先端のAI技術と韓国美容の専門知識を組み合わせた、
              革新的な美容分析サービスです。あなたの美しさを科学的に分析し、
              パーソナライズされたアドバイスを提供します。
            </p>

            {/* Contact Info */}
            <div className="space-y-3">
              <div className="flex items-center text-sm text-gray-400">
                <EnvelopeIcon className="w-4 h-4 mr-3" />
                support@faceaesthetic.ai
              </div>
              <div className="flex items-center text-sm text-gray-400">
                <PhoneIcon className="w-4 h-4 mr-3" />
                03-1234-5678 (平日 10:00-18:00)
              </div>
              <div className="flex items-center text-sm text-gray-400">
                <MapPinIcon className="w-4 h-4 mr-3" />
                東京都渋谷区恵比寿1-1-1
              </div>
            </div>
          </motion.div>

          {/* Service Links */}
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.6, delay: 0.1 }}
          >
            <h4 className="font-semibold mb-4 text-pink-400">サービス</h4>
            <ul className="space-y-3">
              {footerLinks.service.map((link) => (
                <li key={link.name}>
                  <a
                    href={link.href}
                    className="text-gray-400 hover:text-pink-400 transition-colors duration-200 text-sm"
                  >
                    {link.name}
                  </a>
                </li>
              ))}
            </ul>
          </motion.div>

          {/* Support Links */}
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.6, delay: 0.2 }}
          >
            <h4 className="font-semibold mb-4 text-pink-400">サポート</h4>
            <ul className="space-y-3">
              {footerLinks.support.map((link) => (
                <li key={link.name}>
                  <a
                    href={link.href}
                    className="text-gray-400 hover:text-pink-400 transition-colors duration-200 text-sm"
                  >
                    {link.name}
                  </a>
                </li>
              ))}
            </ul>
          </motion.div>

          {/* Company Links */}
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.6, delay: 0.3 }}
          >
            <h4 className="font-semibold mb-4 text-pink-400">会社情報</h4>
            <ul className="space-y-3">
              {footerLinks.company.map((link) => (
                <li key={link.name}>
                  <a
                    href={link.href}
                    className="text-gray-400 hover:text-pink-400 transition-colors duration-200 text-sm"
                  >
                    {link.name}
                  </a>
                </li>
              ))}
            </ul>

            {/* Social Links */}
            <div className="mt-6">
              <h5 className="font-medium mb-3 text-sm">フォローする</h5>
              <div className="flex space-x-3">
                {footerLinks.social.map((social) => (
                  <a
                    key={social.name}
                    href={social.href}
                    className="w-8 h-8 bg-gray-800 rounded-lg flex items-center justify-center hover:bg-pink-600 transition-colors duration-200"
                    title={social.name}
                  >
                    <span className="text-sm">{social.icon}</span>
                  </a>
                ))}
              </div>
            </div>
          </motion.div>
        </div>
      </div>

      {/* Newsletter Section */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.6, delay: 0.4 }}
        className="border-t border-gray-800"
      >
        <div className="max-w-7xl mx-auto px-4 py-8">
          <div className="flex flex-col md:flex-row items-center justify-between">
            <div className="mb-4 md:mb-0">
              <h4 className="font-semibold mb-2 text-pink-400">
                美容情報を定期的に受け取る
              </h4>
              <p className="text-gray-400 text-sm">
                最新の美容トレンドとAI分析技術の情報をお届けします
              </p>
            </div>
            
            <div className="flex w-full md:w-auto">
              <input
                type="email"
                placeholder="メールアドレスを入力"
                className="flex-1 md:w-64 px-4 py-2 bg-gray-800 border border-gray-700 rounded-l-lg focus:outline-none focus:ring-2 focus:ring-pink-500 text-white placeholder-gray-400"
              />
              <button className="px-6 py-2 bg-gradient-korean rounded-r-lg hover:opacity-90 transition-opacity duration-200 font-medium">
                登録
              </button>
            </div>
          </div>
        </div>
      </motion.div>

      {/* Bottom Bar */}
      <motion.div
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        transition={{ duration: 0.6, delay: 0.5 }}
        className="border-t border-gray-800 bg-gray-950"
      >
        <div className="max-w-7xl mx-auto px-4 py-6">
          <div className="flex flex-col md:flex-row items-center justify-between text-sm text-gray-400">
            <div className="flex items-center mb-4 md:mb-0">
              <p>© {currentYear} Face Aesthetic AI. All rights reserved.</p>
            </div>
            
            <div className="flex items-center space-x-1">
              <span>Made with</span>
              <HeartIcon className="w-4 h-4 text-pink-500" />
              <span>in Tokyo, Japan</span>
            </div>
          </div>
        </div>
      </motion.div>
    </footer>
  )
}
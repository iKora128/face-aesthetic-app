'use client'

import { motion } from 'framer-motion'
import { 
  ArrowLeftIcon,
  ChatBubbleLeftRightIcon,
  ArrowDownTrayIcon,
  ShareIcon,
  ChartBarIcon,
  SparklesIcon
} from '@heroicons/react/24/outline'
import { toast } from 'react-hot-toast'
import { AnalysisResult, getScoreColor, getScoreBgColor } from '@/types/analysis'
import { useAnalysisReport } from '@/hooks/useAnalysis'
import ScoreDisplay from './ScoreDisplay'
import RadarChart from './RadarChart'
import FeatureBreakdown from './FeatureBreakdown'
import BeautyAdvice from './BeautyAdvice'

interface AnalysisResultsProps {
  result: AnalysisResult
  onStartChat: () => void
  onBackToUpload: () => void
}

export default function AnalysisResults({
  result,
  onStartChat,
  onBackToUpload,
}: AnalysisResultsProps) {
  const { downloadReport, isDownloading } = useAnalysisReport()

  const handleDownloadReport = async () => {
    if (!result.id) {
      toast.error('レポートのダウンロードができません')
      return
    }

    try {
      await downloadReport(result.id)
      toast.success('レポートをダウンロードしました')
    } catch (error) {
      toast.error('レポートのダウンロードに失敗しました')
    }
  }

  const handleShare = async () => {
    if (navigator.share) {
      try {
        await navigator.share({
          title: 'Face Aesthetic AI - 分析結果',
          text: `美容分析の結果: ${result.overall_score.score}点 (${result.overall_score.level})`,
          url: window.location.href,
        })
      } catch (error) {
        // User cancelled or share failed
      }
    } else {
      // Fallback to clipboard
      try {
        await navigator.clipboard.writeText(window.location.href)
        toast.success('URLをクリップボードにコピーしました')
      } catch (error) {
        toast.error('共有に失敗しました')
      }
    }
  }

  return (
    <div className="min-h-screen py-8">
      <div className="max-w-6xl mx-auto px-4">
        {/* Header */}
        <motion.div
          initial={{ opacity: 0, y: -20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.6 }}
          className="flex flex-col sm:flex-row items-start sm:items-center justify-between mb-8"
        >
          <div className="flex items-center mb-4 sm:mb-0">
            <button
              onClick={onBackToUpload}
              className="mr-4 p-2 hover:bg-gray-100 rounded-lg transition-colors duration-200"
            >
              <ArrowLeftIcon className="w-5 h-5 text-gray-600" />
            </button>
            <div>
              <h1 className="text-2xl sm:text-3xl font-bold text-gray-900">
                分析結果
              </h1>
              <p className="text-gray-600 text-sm">
                {new Date(result.timestamp).toLocaleDateString('ja-JP', {
                  year: 'numeric',
                  month: 'long',
                  day: 'numeric',
                  hour: '2-digit',
                  minute: '2-digit',
                })}
              </p>
            </div>
          </div>

          {/* Action Buttons */}
          <div className="flex flex-col sm:flex-row gap-3 w-full sm:w-auto">
            <button
              onClick={onStartChat}
              className="korean-button flex items-center justify-center"
            >
              <ChatBubbleLeftRightIcon className="w-5 h-5 mr-2" />
              AI美容相談
            </button>
            
            <div className="flex gap-2">
              <button
                onClick={handleDownloadReport}
                disabled={isDownloading}
                className="btn-outline flex items-center justify-center px-4 disabled:opacity-50"
              >
                <ArrowDownTrayIcon className="w-5 h-5 mr-2" />
                {isDownloading ? 'DL中...' : 'レポート'}
              </button>
              
              <button
                onClick={handleShare}
                className="btn-outline flex items-center justify-center px-4"
              >
                <ShareIcon className="w-5 h-5" />
              </button>
            </div>
          </div>
        </motion.div>

        {/* Overall Score Section */}
        <motion.div
          initial={{ opacity: 0, scale: 0.95 }}
          animate={{ opacity: 1, scale: 1 }}
          transition={{ duration: 0.6, delay: 0.1 }}
          className="korean-card p-8 mb-8 text-center"
        >
          <div className="mb-6">
            <div className="text-6xl mb-4">{result.overall_score.emoji}</div>
            <h2 className="text-3xl font-bold text-gray-900 mb-2">
              {result.overall_score.level}
            </h2>
            <p className="text-gray-600 text-lg">
              {result.overall_score.description}
            </p>
          </div>

          <ScoreDisplay
            score={result.overall_score.score}
            size="large"
            showLabel={true}
          />

          <div className="mt-6 grid grid-cols-1 sm:grid-cols-3 gap-4">
            <div className="bg-gray-50 rounded-xl p-4">
              <div className="text-sm text-gray-600 mb-1">ティア</div>
              <div className={`text-lg font-bold ${getScoreColor(result.overall_score.score)}`}>
                {result.overall_score.tier}
              </div>
            </div>
            <div className="bg-gray-50 rounded-xl p-4">
              <div className="text-sm text-gray-600 mb-1">分析精度</div>
              <div className="text-lg font-bold text-green-600">
                {result.face_angle.confidence * 100}%
              </div>
            </div>
            <div className="bg-gray-50 rounded-xl p-4">
              <div className="text-sm text-gray-600 mb-1">ランドマーク</div>
              <div className="text-lg font-bold text-blue-600">
                {result.image_info.total_landmarks}点
              </div>
            </div>
          </div>
        </motion.div>

        <div className="grid grid-cols-1 lg:grid-cols-2 gap-8 mb-8">
          {/* Radar Chart */}
          <motion.div
            initial={{ opacity: 0, x: -20 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ duration: 0.6, delay: 0.2 }}
            className="korean-card p-6"
          >
            <div className="flex items-center mb-6">
              <ChartBarIcon className="w-6 h-6 text-pink-500 mr-3" />
              <h3 className="text-xl font-bold text-gray-900">
                総合バランス
              </h3>
            </div>
            <RadarChart result={result} />
          </motion.div>

          {/* Feature Breakdown */}
          <motion.div
            initial={{ opacity: 0, x: 20 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ duration: 0.6, delay: 0.3 }}
            className="korean-card p-6"
          >
            <div className="flex items-center mb-6">
              <SparklesIcon className="w-6 h-6 text-pink-500 mr-3" />
              <h3 className="text-xl font-bold text-gray-900">
                詳細分析
              </h3>
            </div>
            <FeatureBreakdown result={result} />
          </motion.div>
        </div>

        {/* Beauty Advice */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.6, delay: 0.4 }}
        >
          <BeautyAdvice advice={result.beauty_advice} />
        </motion.div>

        {/* Detailed Scores */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.6, delay: 0.5 }}
          className="korean-card p-6 mb-8"
        >
          <h3 className="text-xl font-bold text-gray-900 mb-6">
            詳細スコア
          </h3>
          
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
            {Object.entries(result.overall_score.detailed_scores).map(([key, score]) => (
              <div
                key={key}
                className={`${getScoreBgColor(score)} rounded-xl p-4 border-l-4 border-l-pink-500`}
              >
                <div className="flex items-center justify-between">
                  <div className="text-sm font-medium text-gray-700">
                    {getFeatureName(key)}
                  </div>
                  <div className={`text-lg font-bold ${getScoreColor(score)}`}>
                    {score.toFixed(1)}
                  </div>
                </div>
              </div>
            ))}
          </div>
        </motion.div>

        {/* Next Steps */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.6, delay: 0.6 }}
          className="text-center"
        >
          <div className="bg-gradient-soft rounded-2xl p-8">
            <h3 className="text-2xl font-bold text-gray-900 mb-4">
              次のステップ
            </h3>
            <p className="text-gray-600 mb-6 max-w-2xl mx-auto">
              分析結果をもとに、韓国美容のプロフェッショナルAIがあなた専用のアドバイスを提供します。
              お気軽にご相談ください。
            </p>
            
            <button
              onClick={onStartChat}
              className="korean-button inline-flex items-center"
            >
              <ChatBubbleLeftRightIcon className="w-5 h-5 mr-2" />
              美容相談を始める
            </button>
          </div>
        </motion.div>
      </div>
    </div>
  )
}

function getFeatureName(key: string): string {
  const featureNames: Record<string, string> = {
    'eline': 'Eライン',
    'harmony': 'パーツ調和',
    'symmetry': '対称性',
    'proportions': '顔の比率',
    'vline': 'Vライン',
    'nasolabial': '鼻唇角',
    'dental': '歯列・唇',
    'contour': '輪郭',
    'philtrum_chin': '人中・顎',
  }
  return featureNames[key] || key
}
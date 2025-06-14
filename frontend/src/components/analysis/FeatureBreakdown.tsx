'use client'

import { motion } from 'framer-motion'
import { 
  CheckCircleIcon,
  ExclamationTriangleIcon,
  InformationCircleIcon 
} from '@heroicons/react/24/outline'
import { AnalysisResult, getScoreColor } from '@/types/analysis'

interface FeatureBreakdownProps {
  result: AnalysisResult
}

export default function FeatureBreakdown({ result }: FeatureBreakdownProps) {
  const features = [
    {
      name: 'Eライン',
      status: result.eline.status,
      evaluation: result.eline.evaluation,
      details: `上唇: ${result.eline.upper_lip_distance.toFixed(1)}mm, 下唇: ${result.eline.lower_lip_distance.toFixed(1)}mm`,
      score: extractScore(result.eline, 85),
    },
    {
      name: 'パーツ調和性',
      status: result.facial_harmony.beauty_level,
      evaluation: result.facial_harmony.evaluation,
      details: `調和スコア: ${result.facial_harmony.harmony_score.toFixed(1)}`,
      score: result.facial_harmony.harmony_score,
    },
    {
      name: '顔の対称性',
      status: result.symmetry.evaluation,
      evaluation: result.symmetry.evaluation,
      details: `非対称レベル: ${result.symmetry.asymmetry_level.toFixed(1)}%`,
      score: result.symmetry.symmetry_score,
    },
    {
      name: '顔の比率',
      status: result.proportions.closest_ratio,
      evaluation: result.proportions.evaluation,
      details: `アスペクト比: ${result.proportions.aspect_ratio.toFixed(3)}`,
      score: extractScore(result.proportions, 80),
    },
    {
      name: 'Vライン',
      status: result.vline.sharpness,
      evaluation: result.vline.evaluation,
      details: `顎角: ${result.vline.jaw_angle.toFixed(1)}°`,
      score: result.vline.vline_score,
    },
    {
      name: '鼻唇角',
      status: result.nasolabial_angle.status,
      evaluation: result.nasolabial_angle.evaluation,
      details: `角度: ${result.nasolabial_angle.angle.toFixed(1)}° (${result.nasolabial_angle.ideal_range})`,
      score: extractScore(result.nasolabial_angle, 90),
    },
  ]

  return (
    <div className="space-y-4">
      {features.map((feature, index) => (
        <motion.div
          key={feature.name}
          initial={{ opacity: 0, x: 20 }}
          animate={{ opacity: 1, x: 0 }}
          transition={{ duration: 0.6, delay: 0.1 * index }}
          className="bg-gray-50 rounded-xl p-4 hover:bg-gray-100 transition-colors duration-200"
        >
          <div className="flex items-start justify-between mb-2">
            <div className="flex items-center">
              {getStatusIcon(feature.score)}
              <h4 className="font-semibold text-gray-900 ml-2">
                {feature.name}
              </h4>
            </div>
            <div className={`text-lg font-bold ${getScoreColor(feature.score)}`}>
              {feature.score.toFixed(1)}
            </div>
          </div>

          <div className="mb-2">
            <span className={`inline-block px-3 py-1 rounded-full text-sm font-medium ${getStatusStyle(feature.score)}`}>
              {feature.status}
            </span>
          </div>

          <div className="text-sm text-gray-600 mb-2">
            {feature.evaluation}
          </div>

          <div className="text-xs text-gray-500">
            {feature.details}
          </div>

          {/* Progress bar */}
          <div className="mt-3">
            <div className="w-full bg-gray-200 rounded-full h-2">
              <motion.div
                initial={{ width: 0 }}
                animate={{ width: `${feature.score}%` }}
                transition={{ duration: 1, delay: 0.2 * index }}
                className={`h-2 rounded-full ${getProgressBarColor(feature.score)}`}
              />
            </div>
          </div>
        </motion.div>
      ))}

      {/* Summary */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.6, delay: 0.8 }}
        className="bg-gradient-to-r from-pink-50 to-purple-50 border border-pink-200 rounded-xl p-6 mt-6"
      >
        <div className="flex items-start">
          <InformationCircleIcon className="w-6 h-6 text-pink-600 mr-3 flex-shrink-0 mt-0.5" />
          <div>
            <h4 className="font-semibold text-pink-900 mb-2">
              分析サマリー
            </h4>
            <div className="text-sm text-pink-800 space-y-1">
              <p>• 強みとなる特徴: {getStrengths(features)}</p>
              <p>• 改善の余地がある項目: {getImprovements(features)}</p>
              <p>• 総合的な印象: {getOverallImpression(features)}</p>
            </div>
          </div>
        </div>
      </motion.div>
    </div>
  )
}

function extractScore(data: any, defaultScore: number): number {
  if (typeof data === 'number') return data
  if (data && typeof data === 'object') {
    if ('score' in data) return data.score
    if ('evaluation' in data) {
      const evaluation = data.evaluation.toLowerCase()
      if (evaluation.includes('理想') || evaluation.includes('優秀')) return 90
      if (evaluation.includes('良好')) return 80
      if (evaluation.includes('標準')) return 70
      return 60
    }
  }
  return defaultScore
}

function getStatusIcon(score: number) {
  if (score >= 80) {
    return <CheckCircleIcon className="w-5 h-5 text-green-600" />
  } else if (score >= 60) {
    return <ExclamationTriangleIcon className="w-5 h-5 text-amber-600" />
  } else {
    return <InformationCircleIcon className="w-5 h-5 text-red-600" />
  }
}

function getStatusStyle(score: number): string {
  if (score >= 90) return 'bg-green-100 text-green-800'
  if (score >= 80) return 'bg-pink-100 text-pink-800'
  if (score >= 70) return 'bg-sky-100 text-sky-800'
  if (score >= 60) return 'bg-amber-100 text-amber-800'
  return 'bg-red-100 text-red-800'
}

function getProgressBarColor(score: number): string {
  if (score >= 90) return 'bg-green-500'
  if (score >= 80) return 'bg-pink-500'
  if (score >= 70) return 'bg-sky-500'
  if (score >= 60) return 'bg-amber-500'
  return 'bg-red-500'
}

function getStrengths(features: Array<{ name: string; score: number }>): string {
  const strongFeatures = features
    .filter(f => f.score >= 80)
    .map(f => f.name)
    .slice(0, 3)
  
  return strongFeatures.length > 0 
    ? strongFeatures.join('、') 
    : '個性的な美しさ'
}

function getImprovements(features: Array<{ name: string; score: number }>): string {
  const improvableFeatures = features
    .filter(f => f.score < 75)
    .map(f => f.name)
    .slice(0, 2)
  
  return improvableFeatures.length > 0 
    ? improvableFeatures.join('、') 
    : 'なし（優秀なバランス）'
}

function getOverallImpression(features: Array<{ name: string; score: number }>): string {
  const averageScore = features.reduce((sum, f) => sum + f.score, 0) / features.length
  
  if (averageScore >= 85) {
    return '非常にバランスの取れた美しい顔立ち'
  } else if (averageScore >= 75) {
    return '魅力的で調和の取れた美しさ'
  } else if (averageScore >= 65) {
    return '個性的で改善の余地がある美しさ'
  } else {
    return 'ユニークな特徴を持つ個性的な美しさ'
  }
}
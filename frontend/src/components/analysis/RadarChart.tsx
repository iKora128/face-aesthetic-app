'use client'

import { motion } from 'framer-motion'
import { 
  Radar, 
  RadarChart as RechartsRadarChart, 
  PolarGrid, 
  PolarAngleAxis, 
  PolarRadiusAxis, 
  ResponsiveContainer 
} from 'recharts'
import { AnalysisResult } from '@/types/analysis'

interface RadarChartProps {
  result: AnalysisResult
}

export default function RadarChart({ result }: RadarChartProps) {
  // Extract scores from analysis result
  const data = [
    {
      category: 'Eライン',
      score: extractScore(result.eline, 85),
      fullMark: 100,
    },
    {
      category: 'パーツ調和',
      score: result.facial_harmony.harmony_score,
      fullMark: 100,
    },
    {
      category: '対称性',
      score: result.symmetry.symmetry_score,
      fullMark: 100,
    },
    {
      category: '顔の比率',
      score: extractScore(result.proportions, 80),
      fullMark: 100,
    },
    {
      category: 'Vライン',
      score: result.vline.vline_score,
      fullMark: 100,
    },
    {
      category: '鼻唇角',
      score: extractScore(result.nasolabial_angle, 90),
      fullMark: 100,
    },
  ]

  return (
    <motion.div
      initial={{ opacity: 0, scale: 0.9 }}
      animate={{ opacity: 1, scale: 1 }}
      transition={{ duration: 0.8 }}
      className="w-full h-80"
    >
      <ResponsiveContainer width="100%" height="100%">
        <RechartsRadarChart data={data}>
          <PolarGrid
            strokeDasharray="3 3"
            stroke="#e5e7eb"
            gridType="polygon"
          />
          <PolarAngleAxis
            dataKey="category"
            tick={{ fontSize: 12, fill: '#6b7280' }}
            className="text-sm font-medium"
          />
          <PolarRadiusAxis
            angle={90}
            domain={[0, 100]}
            tick={{ fontSize: 10, fill: '#9ca3af' }}
            tickCount={5}
          />
          <Radar
            name="スコア"
            dataKey="score"
            stroke="#ec4899"
            fill="#ec4899"
            fillOpacity={0.1}
            strokeWidth={3}
            dot={{ r: 5, fill: '#ec4899', strokeWidth: 2, stroke: '#ffffff' }}
          />
        </RechartsRadarChart>
      </ResponsiveContainer>

      {/* Legend */}
      <div className="mt-4 grid grid-cols-2 gap-2 text-sm">
        {data.map((item, index) => (
          <motion.div
            key={item.category}
            initial={{ opacity: 0, x: -10 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ duration: 0.6, delay: 0.1 * index }}
            className="flex items-center justify-between bg-gray-50 rounded-lg p-2"
          >
            <span className="text-gray-700 font-medium">
              {item.category}
            </span>
            <span className={`font-bold ${getScoreColor(item.score)}`}>
              {item.score.toFixed(1)}
            </span>
          </motion.div>
        ))}
      </div>

      {/* Summary */}
      <motion.div
        initial={{ opacity: 0, y: 10 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.6, delay: 0.8 }}
        className="mt-4 bg-pink-50 border border-pink-200 rounded-xl p-4"
      >
        <div className="text-sm text-pink-800">
          <div className="font-semibold mb-1">バランス評価</div>
          <div>
            {getBalanceEvaluation(data)}
          </div>
        </div>
      </motion.div>
    </motion.div>
  )
}

function extractScore(data: any, defaultScore: number = 70): number {
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

function getScoreColor(score: number): string {
  if (score >= 90) return 'text-green-600'
  if (score >= 80) return 'text-pink-600'
  if (score >= 70) return 'text-sky-600'
  if (score >= 60) return 'text-amber-600'
  return 'text-red-600'
}

function getBalanceEvaluation(data: Array<{ category: string; score: number }>): string {
  const scores = data.map(item => item.score)
  const average = scores.reduce((sum, score) => sum + score, 0) / scores.length
  const variance = scores.reduce((sum, score) => sum + Math.pow(score - average, 2), 0) / scores.length
  const standardDeviation = Math.sqrt(variance)

  if (standardDeviation < 5) {
    return '非常にバランスの取れた美しい顔立ちです。全ての項目が調和しています。'
  } else if (standardDeviation < 10) {
    return 'バランスの良い美しさです。一部に改善の余地があります。'
  } else if (standardDeviation < 15) {
    return '特定の美しい特徴がある一方で、改善できる部分もあります。'
  } else {
    return '個性的な美しさです。特定の特徴を活かすスタイリングがおすすめです。'
  }
}
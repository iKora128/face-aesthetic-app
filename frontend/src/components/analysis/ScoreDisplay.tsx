'use client'

import { motion } from 'framer-motion'
import { getScoreColor } from '@/types/analysis'

interface ScoreDisplayProps {
  score: number
  size?: 'small' | 'medium' | 'large'
  showLabel?: boolean
  className?: string
}

export default function ScoreDisplay({
  score,
  size = 'medium',
  showLabel = false,
  className = '',
}: ScoreDisplayProps) {
  const sizeClasses = {
    small: 'w-16 h-16 text-lg',
    medium: 'w-24 h-24 text-2xl',
    large: 'w-32 h-32 text-3xl',
  }

  const labelSizes = {
    small: 'text-xs',
    medium: 'text-sm',
    large: 'text-base',
  }

  const strokeWidth = {
    small: 4,
    medium: 6,
    large: 8,
  }

  const radius = {
    small: 28,
    medium: 42,
    large: 56,
  }

  const circumference = 2 * Math.PI * radius[size]
  const strokeDasharray = circumference
  const strokeDashoffset = circumference - (score / 100) * circumference

  return (
    <div className={`flex flex-col items-center ${className}`}>
      <div className="relative">
        <svg
          className={`${sizeClasses[size]} transform -rotate-90`}
          viewBox={`0 0 ${radius[size] * 2 + strokeWidth[size] * 2} ${radius[size] * 2 + strokeWidth[size] * 2}`}
        >
          {/* Background circle */}
          <circle
            cx={radius[size] + strokeWidth[size]}
            cy={radius[size] + strokeWidth[size]}
            r={radius[size]}
            stroke="currentColor"
            strokeWidth={strokeWidth[size]}
            fill="none"
            className="text-gray-200"
          />
          
          {/* Progress circle */}
          <motion.circle
            cx={radius[size] + strokeWidth[size]}
            cy={radius[size] + strokeWidth[size]}
            r={radius[size]}
            stroke="currentColor"
            strokeWidth={strokeWidth[size]}
            fill="none"
            strokeLinecap="round"
            strokeDasharray={strokeDasharray}
            strokeDashoffset={strokeDashoffset}
            className={getScoreColor(score)}
            initial={{ strokeDashoffset: circumference }}
            animate={{ strokeDashoffset }}
            transition={{ duration: 1.5, ease: "easeOut", delay: 0.5 }}
          />
        </svg>
        
        {/* Score text */}
        <div className="absolute inset-0 flex items-center justify-center">
          <motion.div
            initial={{ scale: 0 }}
            animate={{ scale: 1 }}
            transition={{ duration: 0.8, delay: 1.2 }}
            className={`font-bold ${getScoreColor(score)} ${sizeClasses[size].split(' ')[2]}`}
          >
            {score.toFixed(1)}
          </motion.div>
        </div>
      </div>
      
      {showLabel && (
        <motion.div
          initial={{ opacity: 0, y: 10 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.6, delay: 1.5 }}
          className={`mt-2 text-gray-600 ${labelSizes[size]} text-center`}
        >
          総合スコア
        </motion.div>
      )}
    </div>
  )
}
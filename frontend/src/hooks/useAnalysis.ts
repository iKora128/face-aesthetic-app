'use client'

import { useState } from 'react'
import { useMutation, useQuery } from 'react-query'
import axios from 'axios'
import { AnalysisResult, AnalysisResponse, AnalysisRequest } from '@/types/analysis'
import { useSupabase } from '@/components/providers/SupabaseProvider'

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'

interface UseAnalysisReturn {
  analyzeImage: (file: File, analysisType?: 'full' | 'basic') => Promise<AnalysisResult>
  isLoading: boolean
  error: string | null
}

export function useAnalysis(): UseAnalysisReturn {
  const { user } = useSupabase()
  const [error, setError] = useState<string | null>(null)

  const analysisMutation = useMutation<AnalysisResult, Error, AnalysisRequest>(
    async ({ file, analysis_type = 'full', user_id }) => {
      setError(null)

      const formData = new FormData()
      formData.append('file', file)
      formData.append('analysis_type', analysis_type)
      
      if (user_id) {
        formData.append('user_id', user_id)
      }

      try {
        const response = await axios.post<AnalysisResponse>(
          `${API_BASE_URL}/api/v1/analysis/analyze`,
          formData,
          {
            headers: {
              'Content-Type': 'multipart/form-data',
            },
            timeout: 60000, // 60 seconds timeout
          }
        )

        if (!response.data.success) {
          throw new Error(response.data.message || 'Analysis failed')
        }

        return response.data.data
      } catch (err) {
        if (axios.isAxiosError(err)) {
          if (err.response?.status === 413) {
            throw new Error('ファイルサイズが大きすぎます。10MB以下の画像を選択してください。')
          } else if (err.response?.status === 400) {
            throw new Error('無効な画像ファイルです。JPEG、PNG、WebP形式の画像を選択してください。')
          } else if (err.response?.status === 422) {
            throw new Error('顔が検出されませんでした。正面を向いた明るい写真を使用してください。')
          } else if (err.code === 'ECONNABORTED') {
            throw new Error('分析がタイムアウトしました。もう一度お試しください。')
          } else if (err.response?.data?.message) {
            throw new Error(err.response.data.message)
          }
        }
        throw new Error('分析に失敗しました。しばらく時間をおいてからもう一度お試しください。')
      }
    },
    {
      onError: (error: Error) => {
        setError(error.message)
      },
      onSuccess: () => {
        setError(null)
      },
    }
  )

  const analyzeImage = async (
    file: File, 
    analysisType: 'full' | 'basic' = 'full'
  ): Promise<AnalysisResult> => {
    return analysisMutation.mutateAsync({
      file,
      analysis_type: analysisType,
      user_id: user?.id,
    })
  }

  return {
    analyzeImage,
    isLoading: analysisMutation.isLoading,
    error,
  }
}

// Hook for fetching user's analysis history
export function useAnalysisHistory(userId?: string) {
  const { user } = useSupabase()
  const targetUserId = userId || user?.id

  return useQuery(
    ['analysis-history', targetUserId],
    async () => {
      if (!targetUserId) return []

      const response = await axios.get(
        `${API_BASE_URL}/api/v1/analysis/history`,
        {
          params: { user_id: targetUserId },
          headers: {
            'Authorization': `Bearer ${user?.id}`, // In real app, use proper JWT
          },
        }
      )

      return response.data.data as AnalysisResult[]
    },
    {
      enabled: !!targetUserId,
      staleTime: 5 * 60 * 1000, // 5 minutes
      cacheTime: 10 * 60 * 1000, // 10 minutes
    }
  )
}

// Hook for fetching a specific analysis result
export function useAnalysisDetail(analysisId: string) {
  const { user } = useSupabase()

  return useQuery(
    ['analysis-detail', analysisId],
    async () => {
      const response = await axios.get(
        `${API_BASE_URL}/api/v1/analysis/${analysisId}`,
        {
          headers: {
            'Authorization': `Bearer ${user?.id}`, // In real app, use proper JWT
          },
        }
      )

      return response.data.data as AnalysisResult
    },
    {
      enabled: !!analysisId && !!user,
      staleTime: 10 * 60 * 1000, // 10 minutes
    }
  )
}

// Hook for downloading analysis report
export function useAnalysisReport() {
  const { user } = useSupabase()

  const downloadMutation = useMutation(
    async (analysisId: string) => {
      const response = await axios.get(
        `${API_BASE_URL}/api/v1/analysis/${analysisId}/report`,
        {
          responseType: 'blob',
          headers: {
            'Authorization': `Bearer ${user?.id}`,
          },
        }
      )

      // Create download link
      const url = window.URL.createObjectURL(new Blob([response.data]))
      const link = document.createElement('a')
      link.href = url
      link.setAttribute('download', `face-analysis-report-${analysisId}.png`)
      document.body.appendChild(link)
      link.click()
      link.remove()
      window.URL.revokeObjectURL(url)
    }
  )

  return {
    downloadReport: downloadMutation.mutateAsync,
    isDownloading: downloadMutation.isLoading,
  }
}
'use client'

import { useCallback, useState } from 'react'
import { useDropzone } from 'react-dropzone'
import { motion } from 'framer-motion'
import { 
  CloudArrowUpIcon, 
  PhotoIcon, 
  ExclamationTriangleIcon,
  CheckCircleIcon 
} from '@heroicons/react/24/outline'
import { toast } from 'react-hot-toast'
import { useAnalysis } from '@/hooks/useAnalysis'
import { AnalysisResult } from '@/types/analysis'

interface AnalysisUploadProps {
  onAnalysisComplete: (result: AnalysisResult) => void
  isLoading: boolean
  setIsLoading: (loading: boolean) => void
}

export default function AnalysisUpload({
  onAnalysisComplete,
  isLoading,
  setIsLoading,
}: AnalysisUploadProps) {
  const [uploadedFile, setUploadedFile] = useState<File | null>(null)
  const [previewUrl, setPreviewUrl] = useState<string | null>(null)
  const { analyzeImage } = useAnalysis()

  const onDrop = useCallback((acceptedFiles: File[]) => {
    const file = acceptedFiles[0]
    if (!file) return

    // Validate file
    if (!file.type.startsWith('image/')) {
      toast.error('画像ファイルを選択してください')
      return
    }

    if (file.size > 10 * 1024 * 1024) { // 10MB limit
      toast.error('ファイルサイズは10MB以下にしてください')
      return
    }

    setUploadedFile(file)
    
    // Create preview URL
    const url = URL.createObjectURL(file)
    setPreviewUrl(url)

    toast.success('画像がアップロードされました')
  }, [])

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    accept: {
      'image/*': ['.jpeg', '.jpg', '.png', '.webp']
    },
    multiple: false,
    maxSize: 10 * 1024 * 1024, // 10MB
  })

  const handleAnalyze = async () => {
    if (!uploadedFile) {
      toast.error('分析する画像を選択してください')
      return
    }

    setIsLoading(true)
    
    try {
      const result = await analyzeImage(uploadedFile)
      onAnalysisComplete(result)
      toast.success('分析が完了しました！')
    } catch (error) {
      console.error('Analysis failed:', error)
      toast.error('分析に失敗しました。もう一度お試しください。')
    } finally {
      setIsLoading(false)
    }
  }

  const handleReset = () => {
    setUploadedFile(null)
    if (previewUrl) {
      URL.revokeObjectURL(previewUrl)
      setPreviewUrl(null)
    }
  }

  return (
    <div className="max-w-2xl mx-auto">
      {/* Upload Zone */}
      <motion.div
        initial={{ opacity: 0, scale: 0.95 }}
        animate={{ opacity: 1, scale: 1 }}
        transition={{ duration: 0.6 }}
        className="korean-card mb-8"
      >
        <div className="p-8">
          {!uploadedFile ? (
            <div
              {...getRootProps()}
              className={`upload-zone ${isDragActive ? 'active' : ''}`}
            >
              <input {...getInputProps()} />
              <div className="text-center">
                <CloudArrowUpIcon className="mx-auto h-16 w-16 text-gray-400 mb-4" />
                <div className="text-xl font-semibold text-gray-900 mb-2">
                  {isDragActive ? '画像をドロップしてください' : '画像をアップロード'}
                </div>
                <p className="text-gray-600 mb-4">
                  画像をドラッグ&ドロップするか、クリックして選択してください
                </p>
                <div className="flex flex-wrap justify-center gap-2 text-sm text-gray-500">
                  <span className="bg-gray-100 px-3 py-1 rounded-full">JPEG</span>
                  <span className="bg-gray-100 px-3 py-1 rounded-full">PNG</span>
                  <span className="bg-gray-100 px-3 py-1 rounded-full">WebP</span>
                  <span className="bg-gray-100 px-3 py-1 rounded-full">最大10MB</span>
                </div>
              </div>
            </div>
          ) : (
            <div className="text-center">
              {/* Preview */}
              <div className="relative mb-6">
                <img
                  src={previewUrl!}
                  alt="アップロード画像"
                  className="max-w-full max-h-64 mx-auto rounded-xl shadow-lg"
                />
                <div className="absolute top-2 right-2">
                  <CheckCircleIcon className="w-8 h-8 text-green-500 bg-white rounded-full" />
                </div>
              </div>

              {/* File Info */}
              <div className="bg-green-50 border border-green-200 rounded-xl p-4 mb-6">
                <div className="flex items-center justify-center mb-2">
                  <PhotoIcon className="w-5 h-5 text-green-600 mr-2" />
                  <span className="font-medium text-green-800">
                    {uploadedFile.name}
                  </span>
                </div>
                <div className="text-sm text-green-600">
                  {(uploadedFile.size / 1024 / 1024).toFixed(2)} MB
                </div>
              </div>

              {/* Action Buttons */}
              <div className="flex flex-col sm:flex-row gap-4 justify-center">
                <button
                  onClick={handleAnalyze}
                  disabled={isLoading}
                  className="korean-button flex items-center justify-center min-w-[200px] disabled:opacity-50 disabled:cursor-not-allowed"
                >
                  {isLoading ? (
                    <>
                      <div className="loading-spinner w-5 h-5 mr-2" />
                      分析中...
                    </>
                  ) : (
                    <>
                      <CheckCircleIcon className="w-5 h-5 mr-2" />
                      分析を開始
                    </>
                  )}
                </button>
                
                <button
                  onClick={handleReset}
                  disabled={isLoading}
                  className="btn-outline disabled:opacity-50 disabled:cursor-not-allowed"
                >
                  別の画像を選択
                </button>
              </div>
            </div>
          )}
        </div>
      </motion.div>

      {/* Guidelines */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.6, delay: 0.2 }}
        className="bg-blue-50 border border-blue-200 rounded-xl p-6"
      >
        <div className="flex items-start mb-4">
          <ExclamationTriangleIcon className="w-6 h-6 text-blue-600 mr-3 flex-shrink-0 mt-0.5" />
          <div>
            <h3 className="font-semibold text-blue-900 mb-2">
              より正確な分析のためのガイドライン
            </h3>
            <ul className="space-y-2 text-sm text-blue-800">
              <li className="flex items-start">
                <span className="w-2 h-2 bg-blue-400 rounded-full mt-2 mr-3 flex-shrink-0" />
                正面を向いた、表情のない状態の写真を使用してください
              </li>
              <li className="flex items-start">
                <span className="w-2 h-2 bg-blue-400 rounded-full mt-2 mr-3 flex-shrink-0" />
                顔全体がはっきりと見える、十分な明るさの写真を選んでください
              </li>
              <li className="flex items-start">
                <span className="w-2 h-2 bg-blue-400 rounded-full mt-2 mr-3 flex-shrink-0" />
                髪の毛やアクセサリーで顔の輪郭が隠れていない写真が理想的です
              </li>
              <li className="flex items-start">
                <span className="w-2 h-2 bg-blue-400 rounded-full mt-2 mr-3 flex-shrink-0" />
                メイクは薄め、または素顔の状態が最も正確な結果を得られます
              </li>
            </ul>
          </div>
        </div>
      </motion.div>

      {/* Loading State */}
      {isLoading && (
        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          className="fixed inset-0 bg-black/50 backdrop-blur-sm z-50 flex items-center justify-center"
        >
          <div className="korean-card p-8 text-center max-w-md mx-4">
            <div className="loading-spinner w-12 h-12 mx-auto mb-4" />
            <h3 className="text-xl font-semibold text-gray-900 mb-2">
              AI分析中...
            </h3>
            <p className="text-gray-600 mb-4">
              あなたの美しさを詳細に分析しています
            </p>
            <div className="w-full bg-gray-200 rounded-full h-2">
              <div className="bg-gradient-korean h-2 rounded-full animate-pulse" style={{ width: '60%' }} />
            </div>
          </div>
        </motion.div>
      )}
    </div>
  )
}
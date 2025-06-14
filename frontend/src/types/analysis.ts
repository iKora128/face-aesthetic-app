// Analysis result types based on backend models

export interface OverallScore {
  score: number
  level: string
  tier: string
  description: string
  emoji: string
  detailed_scores: Record<string, number>
  score_breakdown: Record<string, string>
  severe_flaws: string[]
  explanation_details: {
    strong_points: string[]
    weak_points: string[]
    bonus_factors: string[]
    penalty_factors: string[]
    improvement_suggestions: string[]
  }
  note: string
}

export interface FaceAngle {
  angle: string
  ratio: number
  confidence: number
  suitable_for_analysis: boolean
}

export interface FaceContour {
  face_area: number
  face_perimeter: number
  face_width: number
  face_height: number
  small_face_score: number
  cheekbone_width: number
  jaw_width: number
  cheek_jaw_ratio: number
  vline_evaluation: string
}

export interface ELine {
  status: string
  upper_lip_distance: number
  lower_lip_distance: number
  evaluation: string
}

export interface Proportions {
  aspect_ratio: number
  closest_ratio: string
  ideal_ratio: number
  difference: number
  evaluation: string
}

export interface PhiltrumChin {
  philtrum_length: number
  chin_length: number
  ratio: number
  closest_ideal: string
  target_ratio: number
  difference: number
  evaluation: string
}

export interface NasolabialAngle {
  angle: number
  ideal_range: string
  status: string
  evaluation: string
}

export interface VLine {
  jaw_angle: number
  sharpness: string
  evaluation: string
  vline_score: number
}

export interface Symmetry {
  symmetry_score: number
  asymmetry_level: number
  evaluation: string
}

export interface DentalProtrusion {
  max_upper_protrusion: number
  max_lower_protrusion: number
  avg_upper_protrusion: number
  avg_lower_protrusion: number
  lip_status: string
  dental_status: string
  teeth_visible: boolean
  severity: string
  lip_balance: string
  ideal_range: string
  evaluation: string
}

export interface FacialHarmony {
  avg_eye_width: number
  nose_width: number
  mouth_width: number
  face_width: number
  face_height: number
  face_area: number
  eye_face_ratio: number
  nose_face_ratio: number
  mouth_face_ratio: number
  eye_area_ratio: number
  golden_deviation: number
  face_aspect_ratio: number
  harmony_score: number
  evaluation: string
  beauty_level: string
  explanation: string
}

export interface ImageInfo {
  filename: string
  dimensions: string
  total_landmarks: number
}

export interface AnalysisResult {
  id?: string
  timestamp: string
  image_info: ImageInfo
  face_angle: FaceAngle
  face_contour: FaceContour
  eline: ELine
  proportions: Proportions
  philtrum_chin: PhiltrumChin
  nasolabial_angle: NasolabialAngle
  vline: VLine
  symmetry: Symmetry
  dental_protrusion: DentalProtrusion
  facial_harmony: FacialHarmony
  overall_score: OverallScore
  beauty_advice: string[]
  report_image_url?: string
}

// API Response types
export interface AnalysisResponse {
  success: boolean
  message: string
  data: AnalysisResult
  processing_time_ms: number
}

export interface AnalysisRequest {
  file: File
  analysis_type?: 'full' | 'basic'
  user_id?: string
}

// UI State types
export interface AnalysisState {
  isLoading: boolean
  error: string | null
  result: AnalysisResult | null
  currentStep: 'upload' | 'analyzing' | 'results' | 'chat'
}

// Score level mapping
export const SCORE_LEVELS = {
  SSS: { min: 95, color: 'text-green-500', bgColor: 'bg-green-100' },
  SS: { min: 90, color: 'text-green-500', bgColor: 'bg-green-100' },
  S: { min: 85, color: 'text-pink-500', bgColor: 'bg-pink-100' },
  A: { min: 80, color: 'text-pink-500', bgColor: 'bg-pink-100' },
  B: { min: 75, color: 'text-sky-500', bgColor: 'bg-sky-100' },
  C: { min: 70, color: 'text-sky-500', bgColor: 'bg-sky-100' },
  D: { min: 65, color: 'text-amber-500', bgColor: 'bg-amber-100' },
  E: { min: 60, color: 'text-amber-500', bgColor: 'bg-amber-100' },
  F: { min: 50, color: 'text-red-500', bgColor: 'bg-red-100' },
  G: { min: 0, color: 'text-red-500', bgColor: 'bg-red-100' },
} as const

export function getScoreColor(score: number): string {
  if (score >= 90) return 'text-green-500'
  if (score >= 80) return 'text-pink-500'
  if (score >= 70) return 'text-sky-500'
  if (score >= 60) return 'text-amber-500'
  return 'text-red-500'
}

export function getScoreBgColor(score: number): string {
  if (score >= 90) return 'bg-green-100'
  if (score >= 80) return 'bg-pink-100'
  if (score >= 70) return 'bg-sky-100'
  if (score >= 60) return 'bg-amber-100'
  return 'bg-red-100'
}
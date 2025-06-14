// Supabase database types

export interface Database {
  public: {
    Tables: {
      users: {
        Row: {
          id: string
          email: string
          full_name: string | null
          created_at: string
          updated_at: string
          is_active: boolean
          profile_image_url: string | null
          preferences: Record<string, any> | null
          subscription_tier: string
          last_login_at: string | null
        }
        Insert: {
          id?: string
          email: string
          full_name?: string | null
          created_at?: string
          updated_at?: string
          is_active?: boolean
          profile_image_url?: string | null
          preferences?: Record<string, any> | null
          subscription_tier?: string
          last_login_at?: string | null
        }
        Update: {
          id?: string
          email?: string
          full_name?: string | null
          created_at?: string
          updated_at?: string
          is_active?: boolean
          profile_image_url?: string | null
          preferences?: Record<string, any> | null
          subscription_tier?: string
          last_login_at?: string | null
        }
      }
      analysis_results: {
        Row: {
          id: string
          user_id: string
          image_url: string
          image_filename: string
          analysis_type: string
          overall_score: Record<string, any>
          face_angle: Record<string, any>
          face_contour: Record<string, any>
          eline_analysis: Record<string, any>
          proportions_analysis: Record<string, any>
          philtrum_chin_analysis: Record<string, any>
          nasolabial_angle_analysis: Record<string, any>
          vline_analysis: Record<string, any>
          symmetry_analysis: Record<string, any>
          dental_protrusion_analysis: Record<string, any>
          facial_harmony: Record<string, any>
          beauty_advice: string[]
          processing_time_ms: number
          created_at: string
          updated_at: string
          is_public: boolean
          report_image_url: string | null
          metadata: Record<string, any> | null
        }
        Insert: {
          id?: string
          user_id: string
          image_url: string
          image_filename: string
          analysis_type?: string
          overall_score: Record<string, any>
          face_angle: Record<string, any>
          face_contour: Record<string, any>
          eline_analysis: Record<string, any>
          proportions_analysis: Record<string, any>
          philtrum_chin_analysis: Record<string, any>
          nasolabial_angle_analysis: Record<string, any>
          vline_analysis: Record<string, any>
          symmetry_analysis: Record<string, any>
          dental_protrusion_analysis: Record<string, any>
          facial_harmony: Record<string, any>
          beauty_advice: string[]
          processing_time_ms: number
          created_at?: string
          updated_at?: string
          is_public?: boolean
          report_image_url?: string | null
          metadata?: Record<string, any> | null
        }
        Update: {
          id?: string
          user_id?: string
          image_url?: string
          image_filename?: string
          analysis_type?: string
          overall_score?: Record<string, any>
          face_angle?: Record<string, any>
          face_contour?: Record<string, any>
          eline_analysis?: Record<string, any>
          proportions_analysis?: Record<string, any>
          philtrum_chin_analysis?: Record<string, any>
          nasolabial_angle_analysis?: Record<string, any>
          vline_analysis?: Record<string, any>
          symmetry_analysis?: Record<string, any>
          dental_protrusion_analysis?: Record<string, any>
          facial_harmony?: Record<string, any>
          beauty_advice?: string[]
          processing_time_ms?: number
          created_at?: string
          updated_at?: string
          is_public?: boolean
          report_image_url?: string | null
          metadata?: Record<string, any> | null
        }
      }
      chat_sessions: {
        Row: {
          id: string
          user_id: string
          title: string
          context_type: string
          analysis_id: string | null
          is_active: boolean
          message_count: number
          conversation_context: Record<string, any>
          metadata: Record<string, any>
          created_at: string
          updated_at: string
        }
        Insert: {
          id?: string
          user_id: string
          title: string
          context_type?: string
          analysis_id?: string | null
          is_active?: boolean
          message_count?: number
          conversation_context?: Record<string, any>
          metadata?: Record<string, any>
          created_at?: string
          updated_at?: string
        }
        Update: {
          id?: string
          user_id?: string
          title?: string
          context_type?: string
          analysis_id?: string | null
          is_active?: boolean
          message_count?: number
          conversation_context?: Record<string, any>
          metadata?: Record<string, any>
          created_at?: string
          updated_at?: string
        }
      }
      chat_messages: {
        Row: {
          id: string
          session_id: string
          role: string
          content: string
          analysis_reference: string | null
          model_used: string | null
          tokens_used: number | null
          response_time_ms: number | null
          metadata: Record<string, any>
          created_at: string
        }
        Insert: {
          id?: string
          session_id: string
          role: string
          content: string
          analysis_reference?: string | null
          model_used?: string | null
          tokens_used?: number | null
          response_time_ms?: number | null
          metadata?: Record<string, any>
          created_at?: string
        }
        Update: {
          id?: string
          session_id?: string
          role?: string
          content?: string
          analysis_reference?: string | null
          model_used?: string | null
          tokens_used?: number | null
          response_time_ms?: number | null
          metadata?: Record<string, any>
          created_at?: string
        }
      }
      user_usage: {
        Row: {
          id: string
          user_id: string
          analysis_count: number
          chat_message_count: number
          storage_used_mb: number
          last_analysis_at: string | null
          subscription_start_date: string | null
          subscription_end_date: string | null
          created_at: string
          updated_at: string
        }
        Insert: {
          id?: string
          user_id: string
          analysis_count?: number
          chat_message_count?: number
          storage_used_mb?: number
          last_analysis_at?: string | null
          subscription_start_date?: string | null
          subscription_end_date?: string | null
          created_at?: string
          updated_at?: string
        }
        Update: {
          id?: string
          user_id?: string
          analysis_count?: number
          chat_message_count?: number
          storage_used_mb?: number
          last_analysis_at?: string | null
          subscription_start_date?: string | null
          subscription_end_date?: string | null
          created_at?: string
          updated_at?: string
        }
      }
      line_bot_users: {
        Row: {
          id: string
          line_user_id: string
          user_id: string | null
          display_name: string | null
          picture_url: string | null
          status_message: string | null
          language: string
          is_active: boolean
          created_at: string
          updated_at: string
          last_interaction_at: string | null
        }
        Insert: {
          id?: string
          line_user_id: string
          user_id?: string | null
          display_name?: string | null
          picture_url?: string | null
          status_message?: string | null
          language?: string
          is_active?: boolean
          created_at?: string
          updated_at?: string
          last_interaction_at?: string | null
        }
        Update: {
          id?: string
          line_user_id?: string
          user_id?: string | null
          display_name?: string | null
          picture_url?: string | null
          status_message?: string | null
          language?: string
          is_active?: boolean
          created_at?: string
          updated_at?: string
          last_interaction_at?: string | null
        }
      }
      analysis_feedback: {
        Row: {
          id: string
          analysis_id: string
          user_id: string
          rating: number
          feedback_text: string | null
          feedback_type: string
          is_helpful: boolean | null
          created_at: string
        }
        Insert: {
          id?: string
          analysis_id: string
          user_id: string
          rating: number
          feedback_text?: string | null
          feedback_type?: string
          is_helpful?: boolean | null
          created_at?: string
        }
        Update: {
          id?: string
          analysis_id?: string
          user_id?: string
          rating?: number
          feedback_text?: string | null
          feedback_type?: string
          is_helpful?: boolean | null
          created_at?: string
        }
      }
    }
    Views: {
      [_ in never]: never
    }
    Functions: {
      [_ in never]: never
    }
    Enums: {
      [_ in never]: never
    }
  }
}
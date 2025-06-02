import { createClient } from '@supabase/supabase-js'

const supabaseUrl = 'https://yldykoemvcthucgdaskj.supabase.co'
const supabaseAnonKey = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InlsZHlrb2VtdmN0aHVjZ2Rhc2tqIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NDg4MzgyMzcsImV4cCI6MjA2NDQxNDIzN30.eJoC2kVpZzE5lD8-tbFq9ZokomlWagg1sr8PJ0yo4Mw'

export const supabase = createClient(supabaseUrl, supabaseAnonKey)

export type Database = {
  public: {
    Tables: {
      user_profiles: {
        Row: {
          id: string
          email: string
          full_name: string | null
          created_at: string
          updated_at: string
        }
        Insert: {
          id: string
          email: string
          full_name?: string | null
          created_at?: string
          updated_at?: string
        }
        Update: {
          id?: string
          email?: string
          full_name?: string | null
          created_at?: string
          updated_at?: string
        }
      }
      documents: {
        Row: {
          id: string
          user_id: string
          filename: string
          content_type: string | null
          size_bytes: number | null
          extracted_text: string | null
          status: string
          file_url: string | null
          created_at: string
          updated_at: string
        }
        Insert: {
          id?: string
          user_id: string
          filename: string
          content_type?: string | null
          size_bytes?: number | null
          extracted_text?: string | null
          status?: string
          file_url?: string | null
          created_at?: string
          updated_at?: string
        }
        Update: {
          id?: string
          user_id?: string
          filename?: string
          content_type?: string | null
          size_bytes?: number | null
          extracted_text?: string | null
          status?: string
          file_url?: string | null
          created_at?: string
          updated_at?: string
        }
      }
      chat_sessions: {
        Row: {
          id: string
          user_id: string
          title: string | null
          created_at: string
          updated_at: string
        }
        Insert: {
          id?: string
          user_id: string
          title?: string | null
          created_at?: string
          updated_at?: string
        }
        Update: {
          id?: string
          user_id?: string
          title?: string | null
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
          document_ids: string[] | null
          created_at: string
        }
        Insert: {
          id?: string
          session_id: string
          role: string
          content: string
          document_ids?: string[] | null
          created_at?: string
        }
        Update: {
          id?: string
          session_id?: string
          role?: string
          content?: string
          document_ids?: string[] | null
          created_at?: string
        }
      }
      user_api_keys: {
        Row: {
          id: string
          user_id: string
          provider: string
          encrypted_key: string
          created_at: string
          updated_at: string
        }
        Insert: {
          id?: string
          user_id: string
          provider: string
          encrypted_key: string
          created_at?: string
          updated_at?: string
        }
        Update: {
          id?: string
          user_id?: string
          provider?: string
          encrypted_key?: string
          created_at?: string
          updated_at?: string
        }
      }
    }
  }
}

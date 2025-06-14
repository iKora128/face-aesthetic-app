import type { Metadata } from 'next'
import { Inter, Noto_Sans_JP } from 'next/font/google'
import { Toaster } from 'react-hot-toast'
import QueryProvider from '@/components/providers/QueryProvider'
import SupabaseProvider from '@/components/providers/SupabaseProvider'
import './globals.css'

const inter = Inter({ subsets: ['latin'], variable: '--font-inter' })
const notoSansJP = Noto_Sans_JP({ 
  subsets: ['latin'], 
  variable: '--font-noto-sans-jp',
  weight: ['300', '400', '500', '700']
})

export const metadata: Metadata = {
  title: 'Face Aesthetic AI - 顔面美容分析',
  description: '最新AI技術による詳細な顔面美容分析サービス。K-Beautyトレンドに基づいた美容コンサルテーション。',
  keywords: ['美容分析', 'AI', '韓国美容', 'フェイス分析', 'ビューティー'],
  authors: [{ name: 'Face Aesthetic AI Team' }],
  openGraph: {
    title: 'Face Aesthetic AI',
    description: '最新AI技術による顔面美容分析',
    type: 'website',
    locale: 'ja_JP',
  },
  viewport: 'width=device-width, initial-scale=1',
  robots: 'index, follow',
}

export default function RootLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <html lang="ja" className={`${inter.variable} ${notoSansJP.variable}`}>
      <body className="min-h-screen bg-gradient-to-br from-pink-50 via-white to-purple-50 font-sans antialiased">
        <SupabaseProvider>
          <QueryProvider>
            <div className="relative min-h-screen">
              {/* Background Pattern */}
              <div className="absolute inset-0 bg-grid-pattern opacity-5" />
              
              {/* Main Content */}
              <div className="relative z-10">
                {children}
              </div>
            </div>
            
            {/* Toast Notifications */}
            <Toaster
              position="top-right"
              toastOptions={{
                duration: 4000,
                style: {
                  background: '#ffffff',
                  color: '#1f2937',
                  boxShadow: '0 10px 25px -3px rgba(0, 0, 0, 0.1), 0 4px 6px -2px rgba(0, 0, 0, 0.05)',
                  border: '1px solid #e5e7eb',
                  borderRadius: '12px',
                  padding: '16px',
                  fontSize: '14px',
                  fontWeight: '500',
                },
                success: {
                  style: {
                    borderColor: '#10b981',
                  },
                  iconTheme: {
                    primary: '#10b981',
                    secondary: '#ffffff',
                  },
                },
                error: {
                  style: {
                    borderColor: '#ef4444',
                  },
                  iconTheme: {
                    primary: '#ef4444',
                    secondary: '#ffffff',
                  },
                },
              }}
            />
          </QueryProvider>
        </SupabaseProvider>
      </body>
    </html>
  )
}
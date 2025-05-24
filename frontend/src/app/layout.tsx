import type { Metadata } from 'next';
import { Inter } from 'next/font/google';
import './globals.css';
import { Providers } from '@/components/providers';
import { Toaster } from 'react-hot-toast';

const inter = Inter({ subsets: ['latin'] });

export const metadata: Metadata = {
  title: 'PlaybookWiz - Brand Playbook Intelligence',
  description: 'Intelligent brand playbook processing and analysis platform',
  keywords: ['brand', 'playbook', 'AI', 'intelligence', 'marketing', 'creative'],
  authors: [{ name: 'PlaybookWiz Team' }],
  viewport: 'width=device-width, initial-scale=1',
  robots: 'index, follow',
  openGraph: {
    title: 'PlaybookWiz - Brand Playbook Intelligence',
    description: 'Intelligent brand playbook processing and analysis platform',
    type: 'website',
    locale: 'en_US',
    siteName: 'PlaybookWiz',
  },
  twitter: {
    card: 'summary_large_image',
    title: 'PlaybookWiz - Brand Playbook Intelligence',
    description: 'Intelligent brand playbook processing and analysis platform',
  },
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en" className="h-full">
      <body className={`${inter.className} h-full bg-gray-50 antialiased`}>
        <Providers>
          <div className="min-h-full">
            {children}
          </div>
          <Toaster
            position="top-right"
            toastOptions={{
              duration: 4000,
              style: {
                background: '#363636',
                color: '#fff',
              },
              success: {
                duration: 3000,
                iconTheme: {
                  primary: '#22c55e',
                  secondary: '#fff',
                },
              },
              error: {
                duration: 5000,
                iconTheme: {
                  primary: '#ef4444',
                  secondary: '#fff',
                },
              },
            }}
          />
        </Providers>
      </body>
    </html>
  );
}

import type { Metadata } from 'next'
import { Inter } from 'next/font/google'
import './globals.css'
import { Providers } from './providers'
import EnvironmentInfo from '@/components/debug/EnvironmentInfo'
import '@/lib/api-controls' // Load API controls for console access

const inter = Inter({ subsets: ['latin'] })

export const metadata: Metadata = {
  title: 'Price Regulation Monitoring System',
  description: 'Government price regulation monitoring and enforcement platform',
}

export default function RootLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <html lang="en">
      <body className={inter.className}>
        <Providers>
          {children}
        </Providers>
        <EnvironmentInfo />
      </body>
    </html>
  )
}

import type { Metadata } from 'next'
import { Inter } from 'next/font/google'
import Nav from '@/components/Nav'
import './globals.css'

const inter = Inter({ subsets: ['latin'], variable: '--font-inter' })

export const metadata: Metadata = {
  title: 'Algo Trader',
  description: 'Algorithmic trading research dashboard',
}

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode
}>) {
  return (
    <html lang="en" suppressHydrationWarning className={inter.variable}>
      <body className="bg-[#0a0a0a] text-white min-h-screen antialiased font-sans" suppressHydrationWarning>
        <div className="flex min-h-screen">
          <Nav />
          <main className="flex-1 ml-52 min-h-screen">
            {children}
          </main>
        </div>
      </body>
    </html>
  )
}

import type { Metadata } from 'next'
import { Inter } from 'next/font/google'
import './globals.css'
import { Providers } from './providers'

const inter = Inter({ subsets: ['latin'] })

export const metadata: Metadata = {
  title: 'Doutora IA - Inteligência Jurídica',
  description: 'A maior plataforma de inteligência jurídica do Brasil. Relatórios com IA em minutos.',
  keywords: ['advocacia', 'jurídico', 'IA', 'inteligência artificial', 'análise jurídica'],
  icons: {
    icon: '/favicondoutoraia.png',
  },
  openGraph: {
    title: 'Doutora IA - Inteligência Jurídica',
    description: 'A maior plataforma de inteligência jurídica do Brasil',
    type: 'website',
  },
}

export default function RootLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <html lang="pt-BR">
      <head>
        <link rel="preconnect" href="https://fonts.googleapis.com" />
        <link rel="preconnect" href="https://fonts.gstatic.com" crossOrigin="anonymous" />
        <link href="https://fonts.googleapis.com/css2?family=Cinzel:wght@400;600;700&display=swap" rel="stylesheet" />
      </head>
      <body className={inter.className}>
        <Providers>{children}</Providers>
      </body>
    </html>
  )
}

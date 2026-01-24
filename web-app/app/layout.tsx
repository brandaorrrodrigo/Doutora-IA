import type { Metadata } from 'next'
import { Inter } from 'next/font/google'
import './globals.css'
import { Providers } from './providers'

const inter = Inter({ subsets: ['latin'] })

export const metadata: Metadata = {
  title: 'Doutora IA - Análise Jurídica Inteligente',
  description: 'Relatórios jurídicos com IA em minutos. Legislação, jurisprudência e petições automáticas.',
  keywords: ['advocacia', 'jurídico', 'IA', 'inteligência artificial', 'análise jurídica'],
  openGraph: {
    title: 'Doutora IA - Análise Jurídica Inteligente',
    description: 'Relatórios jurídicos com IA em minutos',
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
      <body className={inter.className}>
        <Providers>{children}</Providers>
      </body>
    </html>
  )
}

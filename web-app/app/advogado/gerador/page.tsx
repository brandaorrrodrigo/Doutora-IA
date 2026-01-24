'use client'

import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import Link from 'next/link'

export default function GeradorPage() {
  return (
    <div className="min-h-screen bg-gray-50">
      <header className="bg-white border-b">
        <div className="container mx-auto px-4 py-4">
          <Link href="/" className="flex items-center space-x-2">
            <span className="text-3xl">⚖️</span>
            <span className="text-xl font-bold">Doutora IA - Gerador de Peças</span>
          </Link>
        </div>
      </header>

      <div className="container mx-auto px-4 py-8 max-w-4xl">
        <h1 className="text-3xl font-bold mb-8">Gerador de Peças Jurídicas</h1>
        
        <div className="grid md:grid-cols-3 gap-4">
          <Card>
            <CardHeader>
              <CardTitle>Inicial - Alimentos</CardTitle>
            </CardHeader>
            <CardContent>
              <Button className="w-full">Gerar Peça</Button>
            </CardContent>
          </Card>

          <Card>
            <CardHeader>
              <CardTitle>Inicial - PIX</CardTitle>
            </CardHeader>
            <CardContent>
              <Button className="w-full">Gerar Peça</Button>
            </CardContent>
          </Card>

          <Card>
            <CardHeader>
              <CardTitle>Inicial - Plano de Saúde</CardTitle>
            </CardHeader>
            <CardContent>
              <Button className="w-full">Gerar Peça</Button>
            </CardContent>
          </Card>
        </div>
      </div>
    </div>
  )
}

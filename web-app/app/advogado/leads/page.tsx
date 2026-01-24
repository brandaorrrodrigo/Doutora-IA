'use client'

import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import Link from 'next/link'

export default function LeadsPage() {
  return (
    <div className="min-h-screen bg-gray-50">
      <header className="bg-white border-b">
        <div className="container mx-auto px-4 py-4">
          <Link href="/" className="flex items-center space-x-2">
            <span className="text-3xl">⚖️</span>
            <span className="text-xl font-bold">Doutora IA - Advogado</span>
          </Link>
        </div>
      </header>

      <div className="container mx-auto px-4 py-8">
        <h1 className="text-3xl font-bold mb-8">Feed de Leads</h1>
        
        <div className="space-y-4">
          <Card>
            <CardHeader>
              <CardTitle>Caso: Pensão Alimentícia</CardTitle>
            </CardHeader>
            <CardContent>
              <p className="text-gray-600 mb-4">
                Área: Família | Probabilidade: Média | Valor estimado: R$ 5.000
              </p>
              <Button>Aceitar Lead</Button>
            </CardContent>
          </Card>
        </div>
      </div>
    </div>
  )
}

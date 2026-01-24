'use client'

import { useState } from 'react'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import Link from 'next/link'

export default function PesquisaPage() {
  const [query, setQuery] = useState('')

  return (
    <div className="min-h-screen bg-gray-50">
      <header className="bg-white border-b">
        <div className="container mx-auto px-4 py-4">
          <Link href="/" className="flex items-center space-x-2">
            <span className="text-3xl">⚖️</span>
            <span className="text-xl font-bold">Doutora IA - Pesquisa</span>
          </Link>
        </div>
      </header>

      <div className="container mx-auto px-4 py-8 max-w-4xl">
        <h1 className="text-3xl font-bold mb-8">Pesquisa Jurídica</h1>
        
        <Card className="mb-6">
          <CardContent className="pt-6">
            <div className="flex gap-2">
              <Input
                placeholder="Buscar legislação, súmulas, jurisprudência..."
                value={query}
                onChange={(e) => setQuery(e.target.value)}
              />
              <Button>Pesquisar</Button>
            </div>
          </CardContent>
        </Card>

        <p className="text-gray-600 text-center">
          Digite sua consulta para buscar em 6 coleções jurídicas
        </p>
      </div>
    </div>
  )
}

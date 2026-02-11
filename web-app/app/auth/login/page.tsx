'use client'

import { useState } from 'react'
import { useRouter } from 'next/navigation'
import { apiClient } from '@/services/api'
import Image from 'next/image'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import Link from 'next/link'

export default function LoginPage() {
  const router = useRouter()
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setLoading(true)
    setError('')

    try {
      const response = await apiClient.login(email, password)
      localStorage.setItem('token', response.data.access_token)
      localStorage.setItem('user', JSON.stringify(response.data.user))
      router.push('/dashboard')
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Erro ao fazer login')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-[#0a0a0a] via-[#1a1410] to-[#0a0a0a] flex items-center justify-center p-4">
      <Card className="w-full max-w-md bg-gradient-to-br from-[#1a1410] to-[#2d1f17] border-2 border-[#d4af37]/40">
        <CardHeader>
          <div className="text-center mb-4">
            <Image src="/logo-redonda.png" alt="Doutora IA" width={80} height={80} className="mx-auto" />
          </div>
          <CardTitle className="text-center text-2xl text-[#d4af37]" style={{ fontFamily: "'Cinzel', serif" }}>Login - Doutora IA</CardTitle>
        </CardHeader>
        <CardContent>
          <form onSubmit={handleSubmit} className="space-y-4">
            <div>
              <Label htmlFor="email">Email</Label>
              <Input
                id="email"
                type="email"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                required
              />
            </div>
            <div>
              <div className="flex justify-between items-center">
                <Label htmlFor="password">Senha</Label>
                <Link href="/auth/forgot-password" className="text-sm text-[#d4af37] hover:underline">
                  Esqueceu a senha?
                </Link>
              </div>
              <Input
                id="password"
                type="password"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                required
              />
            </div>
            {error && (
              <div className="bg-red-50 text-red-600 p-3 rounded-md text-sm">
                {error}
              </div>
            )}
            <Button type="submit" className="w-full bg-gradient-to-r from-[#d4af37] to-[#e6c547] text-[#1a1410] hover:from-[#e6c547] hover:to-[#d4af37] font-bold" disabled={loading}>
              {loading ? 'Entrando...' : 'Entrar'}
            </Button>
            <div className="text-center text-sm text-[#f5f5dc]/70">
              Não tem conta?{' '}
              <Link href="/auth/register" className="text-[#d4af37] hover:underline">
                Cadastre-se
              </Link>
            </div>
          </form>
        </CardContent>
      </Card>
    </div>
  )
}

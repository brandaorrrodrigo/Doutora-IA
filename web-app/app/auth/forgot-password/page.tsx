'use client'

import { useState } from 'react'
import { apiClient } from '@/services/api'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from '@/components/ui/card'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import Link from 'next/link'

export default function ForgotPasswordPage() {
  const [email, setEmail] = useState('')
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')
  const [success, setSuccess] = useState(false)

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setLoading(true)
    setError('')

    try {
      await apiClient.forgotPassword(email)
      setSuccess(true)
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Erro ao enviar email de recuperacao')
    } finally {
      setLoading(false)
    }
  }

  if (success) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-[#0a0a0a] via-[#1a1410] to-[#0a0a0a] flex items-center justify-center p-4">
        <Card className="w-full max-w-md">
          <CardHeader>
            <div className="text-center mb-4">
              <span className="text-5xl">📧</span>
            </div>
            <CardTitle className="text-center text-2xl">Email Enviado!</CardTitle>
            <CardDescription className="text-center">
              Se o email informado estiver cadastrado, voce recebera um link para redefinir sua senha.
            </CardDescription>
          </CardHeader>
          <CardContent>
            <div className="space-y-4">
              <div className="bg-green-50 text-green-700 p-4 rounded-md text-sm">
                Verifique sua caixa de entrada e spam. O link expira em 1 hora.
              </div>
              <Link href="/auth/login">
                <Button variant="outline" className="w-full">
                  Voltar ao Login
                </Button>
              </Link>
            </div>
          </CardContent>
        </Card>
      </div>
    )
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-[#0a0a0a] via-[#1a1410] to-[#0a0a0a] flex items-center justify-center p-4">
      <Card className="w-full max-w-md">
        <CardHeader>
          <div className="text-center mb-4">
            <span className="text-5xl">🔑</span>
          </div>
          <CardTitle className="text-center text-2xl">Esqueci minha senha</CardTitle>
          <CardDescription className="text-center">
            Informe seu email para receber um link de recuperacao
          </CardDescription>
        </CardHeader>
        <CardContent>
          <form onSubmit={handleSubmit} className="space-y-4">
            <div>
              <Label htmlFor="email">Email</Label>
              <Input
                id="email"
                type="email"
                placeholder="seu@email.com"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                required
              />
            </div>
            {error && (
              <div className="bg-red-50 text-red-600 p-3 rounded-md text-sm">
                {error}
              </div>
            )}
            <Button type="submit" className="w-full" disabled={loading}>
              {loading ? 'Enviando...' : 'Enviar link de recuperacao'}
            </Button>
            <div className="text-center text-sm">
              Lembrou a senha?{' '}
              <Link href="/auth/login" className="text-primary hover:underline">
                Fazer login
              </Link>
            </div>
          </form>
        </CardContent>
      </Card>
    </div>
  )
}

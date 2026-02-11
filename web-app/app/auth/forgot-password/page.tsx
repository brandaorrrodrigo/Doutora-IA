'use client'

import { useState } from 'react'
import Image from 'next/image'
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
        <Card className="w-full max-w-md bg-gradient-to-br from-[#1a1410] to-[#2d1f17] border-2 border-[#d4af37]/40">
          <CardHeader>
            <div className="text-center mb-4">
              <Image src="/logo-redonda.png" alt="Doutora IA" width={80} height={80} className="mx-auto" />
            </div>
            <CardTitle className="text-center text-2xl text-[#d4af37]" style={{ fontFamily: "'Cinzel', serif" }}>Email Enviado!</CardTitle>
            <CardDescription className="text-center text-[#f5f5dc]/70">
              Se o email informado estiver cadastrado, voce recebera um link para redefinir sua senha.
            </CardDescription>
          </CardHeader>
          <CardContent>
            <div className="space-y-4">
              <div className="bg-[#d4af37]/10 text-[#d4af37] p-4 rounded-md text-sm border border-[#d4af37]/30">
                Verifique sua caixa de entrada e spam. O link expira em 1 hora.
              </div>
              <Link href="/auth/login">
                <Button variant="outline" className="w-full text-[#d4af37] border-[#d4af37] hover:bg-[#d4af37]/15">
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
      <Card className="w-full max-w-md bg-gradient-to-br from-[#1a1410] to-[#2d1f17] border-2 border-[#d4af37]/40">
        <CardHeader>
          <div className="text-center mb-4">
            <Image src="/logo-redonda.png" alt="Doutora IA" width={80} height={80} className="mx-auto" />
          </div>
          <CardTitle className="text-center text-2xl text-[#d4af37]" style={{ fontFamily: "'Cinzel', serif" }}>Esqueci minha senha</CardTitle>
          <CardDescription className="text-center text-[#f5f5dc]/70">
            Informe seu email para receber um link de recuperacao
          </CardDescription>
        </CardHeader>
        <CardContent>
          <form onSubmit={handleSubmit} className="space-y-4">
            <div>
              <Label htmlFor="email" className="text-[#f5f5dc]">Email</Label>
              <Input
                id="email"
                type="email"
                placeholder="seu@email.com"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                required
                className="bg-[#0a0a0a]/50 border-[#d4af37]/30 text-[#f5f5dc] placeholder:text-[#f5f5dc]/40"
              />
            </div>
            {error && (
              <div className="bg-red-900/30 text-red-300 p-3 rounded-md text-sm border border-red-500/30">
                {error}
              </div>
            )}
            <Button type="submit" className="w-full bg-gradient-to-r from-[#d4af37] to-[#e6c547] text-[#1a1410] hover:from-[#e6c547] hover:to-[#d4af37] font-bold" disabled={loading}>
              {loading ? 'Enviando...' : 'Enviar link de recuperacao'}
            </Button>
            <div className="text-center text-sm">
              Lembrou a senha?{' '}
              <Link href="/auth/login" className="text-[#d4af37] hover:underline">
                Fazer login
              </Link>
            </div>
          </form>
        </CardContent>
      </Card>
    </div>
  )
}

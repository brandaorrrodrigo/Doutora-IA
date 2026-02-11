'use client'

import { useState, useEffect } from 'react'
import { useRouter, useSearchParams } from 'next/navigation'
import Image from 'next/image'
import { apiClient } from '@/services/api'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from '@/components/ui/card'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import Link from 'next/link'

export default function ResetPasswordPage() {
  const router = useRouter()
  const searchParams = useSearchParams()
  const token = searchParams.get('token')

  const [password, setPassword] = useState('')
  const [confirmPassword, setConfirmPassword] = useState('')
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')
  const [success, setSuccess] = useState(false)

  useEffect(() => {
    if (!token) {
      setError('Token de recuperacao invalido ou ausente')
    }
  }, [token])

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setError('')

    if (password !== confirmPassword) {
      setError('As senhas nao coincidem')
      return
    }

    if (password.length < 6) {
      setError('A senha deve ter pelo menos 6 caracteres')
      return
    }

    if (!token) {
      setError('Token de recuperacao invalido')
      return
    }

    setLoading(true)

    try {
      await apiClient.resetPassword(token, password)
      setSuccess(true)
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Erro ao redefinir senha. O token pode ter expirado.')
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
            <CardTitle className="text-center text-2xl text-[#d4af37]" style={{ fontFamily: "'Cinzel', serif" }}>Senha Redefinida!</CardTitle>
            <CardDescription className="text-center text-[#f5f5dc]/70">
              Sua senha foi alterada com sucesso. Voce ja pode fazer login.
            </CardDescription>
          </CardHeader>
          <CardContent>
            <Link href="/auth/login">
              <Button className="w-full bg-gradient-to-r from-[#d4af37] to-[#e6c547] text-[#1a1410] hover:from-[#e6c547] hover:to-[#d4af37] font-bold">
                Ir para Login
              </Button>
            </Link>
          </CardContent>
        </Card>
      </div>
    )
  }

  if (!token) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-[#0a0a0a] via-[#1a1410] to-[#0a0a0a] flex items-center justify-center p-4">
        <Card className="w-full max-w-md bg-gradient-to-br from-[#1a1410] to-[#2d1f17] border-2 border-[#d4af37]/40">
          <CardHeader>
            <div className="text-center mb-4">
              <Image src="/logo-redonda.png" alt="Doutora IA" width={80} height={80} className="mx-auto" />
            </div>
            <CardTitle className="text-center text-2xl text-[#d4af37]" style={{ fontFamily: "'Cinzel', serif" }}>Link Invalido</CardTitle>
            <CardDescription className="text-center text-[#f5f5dc]/70">
              O link de recuperacao e invalido ou expirou.
            </CardDescription>
          </CardHeader>
          <CardContent>
            <div className="space-y-4">
              <Link href="/auth/forgot-password">
                <Button className="w-full bg-gradient-to-r from-[#d4af37] to-[#e6c547] text-[#1a1410] hover:from-[#e6c547] hover:to-[#d4af37] font-bold">
                  Solicitar novo link
                </Button>
              </Link>
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
          <CardTitle className="text-center text-2xl text-[#d4af37]" style={{ fontFamily: "'Cinzel', serif" }}>Redefinir Senha</CardTitle>
          <CardDescription className="text-center text-[#f5f5dc]/70">
            Digite sua nova senha abaixo
          </CardDescription>
        </CardHeader>
        <CardContent>
          <form onSubmit={handleSubmit} className="space-y-4">
            <div>
              <Label htmlFor="password" className="text-[#f5f5dc]">Nova Senha</Label>
              <Input
                id="password"
                type="password"
                placeholder="Minimo 6 caracteres"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                required
                minLength={6}
                className="bg-[#0a0a0a]/50 border-[#d4af37]/30 text-[#f5f5dc] placeholder:text-[#f5f5dc]/40"
              />
            </div>
            <div>
              <Label htmlFor="confirmPassword" className="text-[#f5f5dc]">Confirmar Senha</Label>
              <Input
                id="confirmPassword"
                type="password"
                placeholder="Repita a senha"
                value={confirmPassword}
                onChange={(e) => setConfirmPassword(e.target.value)}
                required
                minLength={6}
                className="bg-[#0a0a0a]/50 border-[#d4af37]/30 text-[#f5f5dc] placeholder:text-[#f5f5dc]/40"
              />
            </div>
            {error && (
              <div className="bg-red-900/30 text-red-300 p-3 rounded-md text-sm border border-red-500/30">
                {error}
              </div>
            )}
            <Button type="submit" className="w-full bg-gradient-to-r from-[#d4af37] to-[#e6c547] text-[#1a1410] hover:from-[#e6c547] hover:to-[#d4af37] font-bold" disabled={loading}>
              {loading ? 'Redefinindo...' : 'Redefinir Senha'}
            </Button>
          </form>
        </CardContent>
      </Card>
    </div>
  )
}

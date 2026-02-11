'use client'

import { useState } from 'react'
import { useRouter } from 'next/navigation'
import { apiClient } from '@/services/api'
import Image from 'next/image'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from '@/components/ui/card'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import Link from 'next/link'

export default function RegisterPage() {
  const router = useRouter()
  const [formData, setFormData] = useState({
    name: '',
    email: '',
    password: '',
    confirmPassword: '',
    oab: '',
    phone: '',
  })
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')

  const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    setFormData({ ...formData, [e.target.name]: e.target.value })
  }

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setError('')

    // Validations
    if (formData.password !== formData.confirmPassword) {
      setError('As senhas nao coincidem')
      return
    }

    if (formData.password.length < 6) {
      setError('A senha deve ter pelo menos 6 caracteres')
      return
    }

    if (formData.oab.length < 5) {
      setError('Informe um numero de OAB valido')
      return
    }

    setLoading(true)

    try {
      await apiClient.register({
        name: formData.name,
        email: formData.email,
        password: formData.password,
        oab: formData.oab,
        phone: formData.phone,
      })
      const loginResponse = await apiClient.login(formData.email, formData.password)
      localStorage.setItem('token', loginResponse.data.access_token)
      localStorage.setItem('user', JSON.stringify(loginResponse.data.user))
      router.push('/dashboard')
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Erro ao cadastrar')
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
          <CardTitle className="text-center text-2xl text-[#d4af37]" style={{ fontFamily: "'Cinzel', serif" }}>Cadastro - Doutora IA</CardTitle>
          <CardDescription className="text-center text-[#f5f5dc]/70">
            Crie sua conta de advogado
          </CardDescription>
        </CardHeader>
        <CardContent>
          <form onSubmit={handleSubmit} className="space-y-4">
            <div>
              <Label htmlFor="name">Nome Completo</Label>
              <Input
                id="name"
                name="name"
                type="text"
                placeholder="Dr. Joao Silva"
                value={formData.name}
                onChange={handleChange}
                required
                minLength={3}
              />
            </div>
            <div>
              <Label htmlFor="email">Email</Label>
              <Input
                id="email"
                name="email"
                type="email"
                placeholder="seu@email.com"
                value={formData.email}
                onChange={handleChange}
                required
              />
            </div>
            <div className="grid grid-cols-2 gap-4">
              <div>
                <Label htmlFor="oab">OAB</Label>
                <Input
                  id="oab"
                  name="oab"
                  type="text"
                  placeholder="SP123456"
                  value={formData.oab}
                  onChange={handleChange}
                  required
                  minLength={5}
                />
              </div>
              <div>
                <Label htmlFor="phone">Telefone</Label>
                <Input
                  id="phone"
                  name="phone"
                  type="tel"
                  placeholder="(11) 99999-9999"
                  value={formData.phone}
                  onChange={handleChange}
                  required
                />
              </div>
            </div>
            <div>
              <Label htmlFor="password">Senha</Label>
              <Input
                id="password"
                name="password"
                type="password"
                placeholder="Minimo 6 caracteres"
                value={formData.password}
                onChange={handleChange}
                required
                minLength={6}
              />
            </div>
            <div>
              <Label htmlFor="confirmPassword">Confirmar Senha</Label>
              <Input
                id="confirmPassword"
                name="confirmPassword"
                type="password"
                placeholder="Repita a senha"
                value={formData.confirmPassword}
                onChange={handleChange}
                required
                minLength={6}
              />
            </div>
            {error && (
              <div className="bg-red-50 text-red-600 p-3 rounded-md text-sm">
                {error}
              </div>
            )}
            <Button type="submit" className="w-full bg-gradient-to-r from-[#d4af37] to-[#e6c547] text-[#1a1410] hover:from-[#e6c547] hover:to-[#d4af37] font-bold" disabled={loading}>
              {loading ? 'Cadastrando...' : 'Criar Conta'}
            </Button>
            <div className="text-center text-sm text-[#f5f5dc]/70">
              Ja tem conta?{' '}
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

import { NextRequest, NextResponse } from 'next/server'
import { registerUser } from '@/lib/auth'
import jwt from 'jsonwebtoken'

const JWT_SECRET = process.env.JWT_SECRET || 'doutora-ia-secret-key-2024-change-in-production'

export async function POST(request: NextRequest) {
  try {
    const body = await request.json()
    const { name, email, password, oab, phone } = body

    if (!name || !email || !password || !oab) {
      return NextResponse.json(
        { detail: 'Campos obrigatorios: name, email, password, oab' },
        { status: 400 }
      )
    }

    if (password.length < 6) {
      return NextResponse.json(
        { detail: 'A senha deve ter pelo menos 6 caracteres' },
        { status: 400 }
      )
    }

    const user = await registerUser({ name, email, password, oab, phone: phone || '' })

    // Gerar token direto (usuario acabou de ser criado, nao precisa re-verificar senha)
    const access_token = jwt.sign(
      { sub: user.id, email: user.email, role: user.role },
      JWT_SECRET,
      { expiresIn: '7d' }
    )

    return NextResponse.json(
      { message: 'Cadastro realizado com sucesso', user, access_token },
      { status: 201 }
    )
  } catch (error: any) {
    const message = error.message || 'Erro ao cadastrar'
    const status = message.includes('ja cadastrad') ? 409 : 500
    return NextResponse.json({ detail: message }, { status })
  }
}

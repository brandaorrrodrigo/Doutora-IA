import { NextRequest, NextResponse } from 'next/server'
import { loginUser } from '@/lib/auth'

export async function POST(request: NextRequest) {
  try {
    const body = await request.json()
    const { email, password } = body

    if (!email || !password) {
      return NextResponse.json(
        { detail: 'Email e senha sao obrigatorios' },
        { status: 400 }
      )
    }

    const result = await loginUser(email, password)

    return NextResponse.json({
      access_token: result.access_token,
      user: result.user,
    })
  } catch (error: any) {
    return NextResponse.json(
      { detail: error.message || 'Email ou senha invalidos' },
      { status: 401 }
    )
  }
}

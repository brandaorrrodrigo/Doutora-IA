import { NextRequest, NextResponse } from 'next/server'
import { query } from '@/lib/db'

export async function POST(request: NextRequest) {
  const authHeader = request.headers.get('authorization')
  const setupToken = process.env.SETUP_TOKEN || 'doutora-setup-2024'

  if (authHeader !== `Bearer ${setupToken}`) {
    return NextResponse.json({ detail: 'Nao autorizado' }, { status: 401 })
  }

  try {
    await query(`
      CREATE TABLE IF NOT EXISTS users (
        id            SERIAL PRIMARY KEY,
        name          VARCHAR(255) NOT NULL,
        email         VARCHAR(255) NOT NULL UNIQUE,
        password_hash VARCHAR(255) NOT NULL,
        oab           VARCHAR(50)  NOT NULL UNIQUE,
        phone         VARCHAR(30)  NOT NULL DEFAULT '',
        role          VARCHAR(20)  NOT NULL DEFAULT 'lawyer',
        created_at    TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW()
      );
    `)

    await query('CREATE INDEX IF NOT EXISTS idx_users_email ON users (email);')
    await query('CREATE INDEX IF NOT EXISTS idx_users_oab   ON users (oab);')

    return NextResponse.json({
      message: 'Tabela users criada com sucesso',
      schema: {
        table: 'users',
        columns: ['id', 'name', 'email', 'password_hash', 'oab', 'phone', 'role', 'created_at'],
        indexes: ['idx_users_email', 'idx_users_oab'],
      },
    })
  } catch (error: any) {
    return NextResponse.json(
      { detail: 'Erro ao criar tabela', error: error.message },
      { status: 500 }
    )
  }
}

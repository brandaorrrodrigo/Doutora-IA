import bcrypt from 'bcryptjs'
import jwt from 'jsonwebtoken'
import { query } from './db'

const JWT_SECRET = process.env.JWT_SECRET || 'doutora-ia-secret-key-2024-change-in-production'

export interface UserRecord {
  id: number
  name: string
  email: string
  password_hash: string
  oab: string
  phone: string
  role: 'user' | 'lawyer' | 'admin'
  created_at: string
}

export type SafeUser = Omit<UserRecord, 'password_hash'>

function toSafeUser(row: UserRecord): SafeUser {
  const { password_hash, ...safe } = row
  return safe
}

export async function registerUser(data: {
  name: string
  email: string
  password: string
  oab: string
  phone: string
}): Promise<SafeUser> {
  const existing = await query(
    'SELECT email, oab FROM users WHERE email = $1 OR oab = $2 LIMIT 1',
    [data.email, data.oab]
  )

  if (existing.rows.length > 0) {
    if (existing.rows[0].email === data.email) {
      throw new Error('Email ja cadastrado')
    }
    throw new Error('OAB ja cadastrada')
  }

  const password_hash = await bcrypt.hash(data.password, 10)

  const result = await query(
    `INSERT INTO users (name, email, password_hash, oab, phone, role)
     VALUES ($1, $2, $3, $4, $5, 'lawyer')
     RETURNING id, name, email, oab, phone, role, created_at`,
    [data.name, data.email, password_hash, data.oab, data.phone || '']
  )

  return result.rows[0] as SafeUser
}

export async function loginUser(
  email: string,
  password: string
): Promise<{ access_token: string; user: SafeUser }> {
  const result = await query(
    'SELECT * FROM users WHERE email = $1 LIMIT 1',
    [email]
  )

  if (result.rows.length === 0) {
    throw new Error('Email ou senha invalidos')
  }

  const user = result.rows[0] as UserRecord

  const isValid = await bcrypt.compare(password, user.password_hash)
  if (!isValid) {
    throw new Error('Email ou senha invalidos')
  }

  const safeUser = toSafeUser(user)
  const access_token = jwt.sign(
    { sub: user.id, email: user.email, role: user.role },
    JWT_SECRET,
    { expiresIn: '7d' }
  )

  return { access_token, user: safeUser }
}

export function verifyToken(token: string): { sub: number; email: string; role: string } {
  return jwt.verify(token, JWT_SECRET) as unknown as { sub: number; email: string; role: string }
}

export async function getUserById(id: number): Promise<SafeUser | null> {
  const result = await query(
    'SELECT id, name, email, oab, phone, role, created_at FROM users WHERE id = $1 LIMIT 1',
    [id]
  )

  if (result.rows.length === 0) return null
  return result.rows[0] as SafeUser
}

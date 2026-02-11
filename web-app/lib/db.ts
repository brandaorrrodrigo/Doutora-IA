import { Pool, PoolConfig } from 'pg'

function getPoolConfig(): PoolConfig {
  const connectionString = process.env.POSTGRES_URL_NON_POOLING || process.env.POSTGRES_URL

  // Remover sslmode da URL para evitar conflito com config programatica
  const cleanUrl = connectionString?.replace(/[?&]sslmode=[^&]*/g, '')

  return {
    connectionString: cleanUrl,
    ssl: process.env.NODE_ENV === 'development'
      ? false
      : { rejectUnauthorized: false },
    max: 5,
  }
}

const pool = new Pool(getPoolConfig())

export async function query(text: string, params?: any[]) {
  const client = await pool.connect()
  try {
    return await client.query(text, params)
  } finally {
    client.release()
  }
}

export default pool

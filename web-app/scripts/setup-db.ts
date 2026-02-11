/**
 * Script de setup do banco de dados Postgres (Supabase/Neon)
 *
 * Uso:
 *   DOTENV_CONFIG_PATH=.env.local npx tsx -r dotenv/config scripts/setup-db.ts
 *
 * Requer variavel de ambiente POSTGRES_URL ou POSTGRES_URL_NON_POOLING configurada.
 */
import { Pool } from 'pg'

async function setup() {
  const connectionString = process.env.POSTGRES_URL_NON_POOLING || process.env.POSTGRES_URL
  if (!connectionString) {
    console.error('ERRO: POSTGRES_URL ou POSTGRES_URL_NON_POOLING nao encontrada.')
    process.exit(1)
  }

  const pool = new Pool({ connectionString, ssl: { rejectUnauthorized: false } })

  console.log('Conectando ao banco...')
  const client = await pool.connect()

  try {
    console.log('Criando tabela users...')
    await client.query(`
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
    console.log('Tabela users criada.')

    await client.query('CREATE INDEX IF NOT EXISTS idx_users_email ON users (email);')
    await client.query('CREATE INDEX IF NOT EXISTS idx_users_oab   ON users (oab);')
    console.log('Indices criados.')

    console.log('Setup concluido!')
  } finally {
    client.release()
    await pool.end()
  }
}

setup()
  .then(() => process.exit(0))
  .catch((err) => {
    console.error('Erro no setup:', err.message)
    process.exit(1)
  })

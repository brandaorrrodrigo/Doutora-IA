import { NextResponse } from 'next/server'
import type { NextRequest } from 'next/server'

const CANONICAL_HOST = 'www.doutoraia.com'

export function middleware(request: NextRequest) {
  const host = request.headers.get('host') || ''

  // Se não está no domínio canônico e não é localhost, redireciona
  if (
    host !== CANONICAL_HOST &&
    !host.startsWith('localhost') &&
    !host.startsWith('127.0.0.1')
  ) {
    const url = new URL(request.url)
    url.host = CANONICAL_HOST
    url.port = ''
    url.protocol = 'https:'
    // 308 preserva o método HTTP (POST continua POST)
    return NextResponse.redirect(url, 308)
  }

  return NextResponse.next()
}

export const config = {
  // Aplica em todas as rotas exceto assets estáticos
  matcher: ['/((?!_next/static|_next/image|favicon.ico|.*\\.png$|.*\\.svg$|.*\\.jpg$).*)'],
}

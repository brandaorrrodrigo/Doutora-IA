'use client';
import Link from 'next/link';
import Image from 'next/image';
import { useState } from 'react';

export default function LoginPage() {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    // Aqui virá a lógica de autenticação
    console.log('Login attempt:', { email, password });
  };

  return (
    <>
      <style jsx global>{`
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body { font-family: 'Georgia', 'Times New Roman', serif; background: #0a0a0a; color: #f5f5dc; line-height: 1.8; }

        .login-container { min-height: 100vh; display: flex; align-items: center; justify-content: center; padding: 20px; background: linear-gradient(135deg, #0a0a0a, #1a1410); }

        .login-box { background: linear-gradient(135deg, #1a1410, #2d1f17); border: 2px solid #d4af37; border-radius: 12px; padding: 50px 40px; max-width: 500px; width: 100%; box-shadow: 0 8px 32px rgba(0, 0, 0, 0.5); }

        .login-header { text-align: center; margin-bottom: 40px; }
        .login-logo { margin-bottom: 30px; display: flex; justify-content: center; }
        .login-title { font-size: 2.5em; color: #d4af37; font-weight: 400; letter-spacing: 2px; margin-bottom: 10px; text-shadow: 0 2px 4px rgba(0,0,0,0.5); }
        .login-subtitle { font-size: 1em; color: #f5f5dc; opacity: 0.9; }

        .login-form { display: flex; flex-direction: column; gap: 25px; }

        .form-group { display: flex; flex-direction: column; gap: 8px; }
        .form-label { font-size: 0.95em; color: #d4af37; font-weight: 500; letter-spacing: 0.5px; }
        .form-input { padding: 14px 18px; background: rgba(10, 10, 10, 0.6); border: 1px solid rgba(212, 175, 55, 0.3); border-radius: 6px; color: #f5f5dc; font-size: 1em; font-family: inherit; transition: all 0.3s; }
        .form-input:focus { outline: none; border-color: #d4af37; background: rgba(10, 10, 10, 0.8); box-shadow: 0 0 0 3px rgba(212, 175, 55, 0.1); }
        .form-input::placeholder { color: rgba(245, 245, 220, 0.4); }

        .forgot-password { text-align: right; }
        .forgot-password a { color: #d4af37; text-decoration: none; font-size: 0.9em; transition: all 0.3s; }
        .forgot-password a:hover { color: #b8860b; text-decoration: underline; }

        .btn-login { padding: 16px; background: #d4af37; color: #1a1410; border: none; border-radius: 6px; font-size: 1.1em; font-weight: 600; cursor: pointer; transition: all 0.3s; font-family: inherit; }
        .btn-login:hover { background: #b8860b; transform: translateY(-2px); box-shadow: 0 4px 12px rgba(212, 175, 55, 0.3); }
        .btn-login:active { transform: translateY(0); }

        .divider { text-align: center; margin: 30px 0; color: rgba(245, 245, 220, 0.5); font-size: 0.9em; position: relative; }
        .divider::before, .divider::after { content: ''; position: absolute; top: 50%; width: 40%; height: 1px; background: rgba(212, 175, 55, 0.2); }
        .divider::before { left: 0; }
        .divider::after { right: 0; }

        .create-account { text-align: center; padding: 20px; background: rgba(212, 175, 55, 0.05); border-radius: 6px; margin-top: 30px; }
        .create-account p { color: #f5f5dc; font-size: 0.95em; margin-bottom: 15px; }
        .btn-create { display: inline-block; padding: 12px 30px; background: transparent; border: 2px solid #d4af37; color: #d4af37; text-decoration: none; border-radius: 6px; font-weight: 600; transition: all 0.3s; }
        .btn-create:hover { background: rgba(212, 175, 55, 0.1); transform: translateY(-2px); }

        .back-home { text-align: center; margin-top: 30px; }
        .back-home a { color: rgba(245, 245, 220, 0.7); text-decoration: none; font-size: 0.9em; transition: all 0.3s; }
        .back-home a:hover { color: #d4af37; }

        @media (max-width: 600px) {
          .login-box { padding: 40px 30px; }
          .login-title { font-size: 2em; }
          .login-logo img { width: 180px !important; height: 180px !important; }
        }
      `}</style>

      <div className="login-container">
        <div className="login-box">
          <div className="login-header">
            <div className="login-logo">
              <Image src="/logodoutoraia.png" alt="Doutora IA" width={250} height={250} priority />
            </div>
            <h1 className="login-title">DOUTORA IA</h1>
            <p className="login-subtitle">Beta Fechado - Acesso por Convite</p>
          </div>

          <form className="login-form" onSubmit={handleSubmit}>
            <div className="form-group">
              <label htmlFor="email" className="form-label">Email</label>
              <input
                id="email"
                type="email"
                className="form-input"
                placeholder="seu@email.com"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                required
              />
            </div>

            <div className="form-group">
              <label htmlFor="password" className="form-label">Senha</label>
              <input
                id="password"
                type="password"
                className="form-input"
                placeholder="••••••••"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                required
              />
            </div>

            <div className="forgot-password">
              <Link href="/recuperar-senha">Esqueci minha senha</Link>
            </div>

            <button type="submit" className="btn-login">
              ENTRAR
            </button>
          </form>

          <div className="divider">ou</div>

          <div className="create-account">
            <p>Ainda não tem acesso ao beta?</p>
            <Link href="/cadastro" className="btn-create">CRIAR CONTA</Link>
          </div>

          <div className="back-home">
            <Link href="/">← Voltar para home</Link>
          </div>
        </div>
      </div>
    </>
  );
}

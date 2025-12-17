'use client';
import React, { useState } from 'react';
import Container from './Container';
import { trackCTAClick } from '@/lib/analytics';

export default function Header() {
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false);

  return (
    <header className="sticky top-0 z-50 bg-background/95 backdrop-blur border-b border-white/10">
      <Container>
        <nav className="flex items-center justify-between py-4" aria-label="Navegação principal">
          <div className="flex items-center gap-2">
            <svg className="w-8 h-8 text-primary" viewBox="0 0 24 24" fill="currentColor" aria-hidden="true">
              <path d="M12 2C10.34 2 9 3.34 9 5C9 6.66 10.34 8 12 8C13.66 8 15 6.66 15 5C15 3.34 13.66 2 12 2ZM12 10C8.13 10 5 13.13 5 17V22H7V17C7 14.24 9.24 12 12 12C14.76 12 17 14.24 17 17V22H19V17C19 13.13 15.87 10 12 10Z"/>
            </svg>
            <span className="text-xl font-bold text-foreground">Doutora IA</span>
          </div>

          <div className="hidden md:flex items-center gap-6">
            <a href="#demo" className="text-sm hover:text-primary transition">Demo</a>
            <a href="#pricing" className="text-sm hover:text-primary transition">Preços</a>
            <a href="#faq" className="text-sm hover:text-primary transition">FAQ</a>
            <button
              onClick={() => {
                trackCTAClick('header_leads');
                document.getElementById('lead-modal')?.classList.remove('hidden');
              }}
              className="px-4 py-2 bg-primary text-background rounded-lg font-semibold hover:bg-primary-dark transition"
            >
              Entrar na fila
            </button>
          </div>

          <button
            className="md:hidden p-2"
            onClick={() => setMobileMenuOpen(!mobileMenuOpen)}
            aria-label="Menu mobile"
            aria-expanded={mobileMenuOpen}
          >
            <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 6h16M4 12h16M4 18h16" />
            </svg>
          </button>
        </nav>

        {mobileMenuOpen && (
          <div className="md:hidden py-4 border-t border-white/10">
            <div className="flex flex-col gap-4">
              <a href="#demo" className="text-sm hover:text-primary transition" onClick={() => setMobileMenuOpen(false)}>Demo</a>
              <a href="#pricing" className="text-sm hover:text-primary transition" onClick={() => setMobileMenuOpen(false)}>Preços</a>
              <a href="#faq" className="text-sm hover:text-primary transition" onClick={() => setMobileMenuOpen(false)}>FAQ</a>
              <button
                onClick={() => {
                  trackCTAClick('header_leads_mobile');
                  document.getElementById('lead-modal')?.classList.remove('hidden');
                  setMobileMenuOpen(false);
                }}
                className="px-4 py-2 bg-primary text-background rounded-lg font-semibold hover:bg-primary-dark transition text-center"
              >
                Entrar na fila
              </button>
            </div>
          </div>
        )}
      </Container>
    </header>
  );
}

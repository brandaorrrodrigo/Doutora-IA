'use client';
import React from 'react';
import Header from '@/components/Header';
import Footer from '@/components/Footer';
import Hero from '@/components/Hero';
import Proof from '@/components/Proof';
import HowItWorks from '@/components/HowItWorks';
import Benefits from '@/components/Benefits';
import Demo from '@/components/Demo';
import Pricing from '@/components/Pricing';
import RoiCalculator from '@/components/RoiCalculator';
import FAQ from '@/components/FAQ';
import CtaFinal from '@/components/CtaFinal';
import LeadModal from '@/components/LeadModal';

export default function HomePage() {
  return (
    <div className="min-h-screen bg-background text-foreground">
      <Header />

      <main>
        <Hero />
        <Proof />
        <HowItWorks />
        <Benefits />
        <Demo />
        <Pricing />
        <RoiCalculator />
        <FAQ />
        <CtaFinal />
      </main>

      <Footer />
      <LeadModal />

      {/* Google Tag Manager / Analytics Script Placeholder */}
      <script
        dangerouslySetInnerHTML={{
          __html: `
            window.dataLayer = window.dataLayer || [];
            // Add your GTM/GA4 initialization here
          `
        }}
      />
    </div>
  );
}

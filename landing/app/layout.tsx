import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "Doutora IA para Advogados — pesquise, redija e receba leads qualificados",
  description: "Jurisprudência e leis com citações auditáveis, gerador de peças com fontes e rodízio de leads por área. LGPD first.",
  openGraph: {
    title: "Doutora IA para Advogados",
    description: "Jurisprudência e leis com citações auditáveis, gerador de peças com fontes e rodízio de leads por área.",
    images: ["/og.jpg"],
    type: "website",
  },
  twitter: {
    card: "summary_large_image",
    title: "Doutora IA para Advogados",
    description: "Jurisprudência e leis com citações auditáveis, gerador de peças com fontes e rodízio de leads por área.",
    images: ["/og.jpg"],
  },
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="pt-BR">
      <head>
        <script
          type="application/ld+json"
          dangerouslySetInnerHTML={{
            __html: JSON.stringify({
              "@context": "https://schema.org",
              "@type": "Product",
              "name": "Doutora IA para Advogados",
              "description": "Jurisprudência e leis com citações auditáveis, gerador de peças com fontes e rodízio de leads por área.",
              "offers": [
                {
                  "@type": "Offer",
                  "name": "Plano Pesquisa",
                  "price": "49",
                  "priceCurrency": "BRL"
                },
                {
                  "@type": "Offer",
                  "name": "Plano Leads",
                  "price": "79",
                  "priceCurrency": "BRL"
                },
                {
                  "@type": "Offer",
                  "name": "Plano Redação",
                  "price": "99",
                  "priceCurrency": "BRL"
                },
                {
                  "@type": "Offer",
                  "name": "Plano Pro",
                  "price": "149",
                  "priceCurrency": "BRL"
                },
                {
                  "@type": "Offer",
                  "name": "Plano Full",
                  "price": "199",
                  "priceCurrency": "BRL"
                }
              ]
            })
          }}
        />
      </head>
      <body>{children}</body>
    </html>
  );
}

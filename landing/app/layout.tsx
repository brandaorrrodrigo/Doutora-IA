import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "Doutora IA - Gestão Jurídica Inteligente",
  description: "Plataforma completa para advogados gerenciarem leads e clientes. Dashboard, gestão de leads e ferramentas essenciais para o dia a dia.",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="pt-BR">
      <body>{children}</body>
    </html>
  );
}

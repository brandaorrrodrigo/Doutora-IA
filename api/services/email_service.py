"""
Serviço de Email SMTP
Envia emails transacionais (verificação, reset de senha, notificações)
"""
import os
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.image import MIMEImage
from typing import List, Optional
from jinja2 import Template


class EmailService:
    """Serviço de envio de emails via SMTP"""

    def __init__(self):
        self.smtp_host = os.getenv("SMTP_HOST", "smtp.gmail.com")
        self.smtp_port = int(os.getenv("SMTP_PORT", "587"))
        self.smtp_user = os.getenv("SMTP_USER", "")
        self.smtp_pass = os.getenv("SMTP_PASS", "")
        self.from_email = os.getenv("FROM_EMAIL", self.smtp_user)
        self.from_name = "Doutora IA"

        self.enabled = bool(self.smtp_user and self.smtp_pass)

        if not self.enabled:
            print("⚠️ SMTP não configurado. Emails serão exibidos no console.")

    def _send_email(
        self,
        to_email: str,
        subject: str,
        html_body: str,
        text_body: Optional[str] = None
    ) -> bool:
        """
        Envia email via SMTP

        Args:
            to_email: Email do destinatário
            subject: Assunto do email
            html_body: Corpo HTML do email
            text_body: Corpo texto plano (fallback)

        Returns:
            True se enviado com sucesso, False caso contrário
        """
        if not self.enabled:
            # Modo debug - imprimir no console
            print(f"""
╔════════════════════════════════════════════════════════════
║ EMAIL (DEBUG MODE - SMTP não configurado)
╠════════════════════════════════════════════════════════════
║ Para: {to_email}
║ Assunto: {subject}
╠════════════════════════════════════════════════════════════
{html_body[:500]}...
╚════════════════════════════════════════════════════════════
            """)
            return True

        try:
            # Criar mensagem
            msg = MIMEMultipart('alternative')
            msg['From'] = f"{self.from_name} <{self.from_email}>"
            msg['To'] = to_email
            msg['Subject'] = subject

            # Adicionar corpo texto plano
            if text_body:
                part1 = MIMEText(text_body, 'plain', 'utf-8')
                msg.attach(part1)

            # Adicionar corpo HTML
            part2 = MIMEText(html_body, 'html', 'utf-8')
            msg.attach(part2)

            # Conectar e enviar
            with smtplib.SMTP(self.smtp_host, self.smtp_port) as server:
                server.starttls()
                server.login(self.smtp_user, self.smtp_pass)
                server.send_message(msg)

            print(f"✓ Email enviado para {to_email}: {subject}")
            return True

        except Exception as e:
            print(f"✗ Erro ao enviar email para {to_email}: {e}")
            return False

    # ==========================================
    # TEMPLATES DE EMAIL
    # ==========================================

    def _get_base_template(self) -> str:
        """Template base HTML para todos os emails"""
        return """
<!DOCTYPE html>
<html lang="pt-BR">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{{ title }}</title>
    <style>
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            line-height: 1.6;
            color: #333;
            max-width: 600px;
            margin: 0 auto;
            padding: 20px;
            background: #f5f7fa;
        }
        .container {
            background: white;
            border-radius: 10px;
            padding: 40px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        }
        .header {
            text-align: center;
            padding-bottom: 20px;
            border-bottom: 3px solid #1a5490;
            margin-bottom: 30px;
        }
        .logo {
            font-size: 2rem;
            font-weight: bold;
            color: #1a5490;
        }
        .button {
            display: inline-block;
            padding: 12px 30px;
            background: #1a5490;
            color: white !important;
            text-decoration: none;
            border-radius: 5px;
            margin: 20px 0;
        }
        .footer {
            text-align: center;
            margin-top: 30px;
            padding-top: 20px;
            border-top: 1px solid #ddd;
            color: #666;
            font-size: 0.9rem;
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <div class="logo">⚖️ DOUTORA IA</div>
            <p style="margin: 5px 0 0 0; color: #666;">Inteligência Artificial Jurídica</p>
        </div>

        {{ content }}

        <div class="footer">
            <p>Este é um email automático. Por favor, não responda.</p>
            <p>
                <a href="https://doutoraia.com.br">doutoraia.com.br</a> |
                <a href="mailto:contato@doutoraia.com.br">contato@doutoraia.com.br</a>
            </p>
        </div>
    </div>
</body>
</html>
        """

    # ==========================================
    # EMAILS ESPECÍFICOS
    # ==========================================

    def send_verification_email(self, to_email: str, lawyer_name: str, token: str) -> bool:
        """
        Envia email de verificação de conta

        Args:
            to_email: Email do advogado
            lawyer_name: Nome do advogado
            token: Token de verificação

        Returns:
            True se enviado com sucesso
        """
        base_url = os.getenv("BASE_URL", "http://localhost:3000")
        verification_url = f"{base_url}/verify-email.html?token={token}"

        content = f"""
        <h2 style="color: #1a5490;">Bem-vindo à Doutora IA, {lawyer_name}! 🎉</h2>

        <p>Obrigado por se cadastrar na plataforma Doutora IA.</p>

        <p>Para ativar sua conta e começar a receber leads qualificados, clique no botão abaixo:</p>

        <p style="text-align: center;">
            <a href="{verification_url}" class="button">Verificar Minha Conta</a>
        </p>

        <p>Ou copie e cole este link no seu navegador:</p>
        <p style="background: #f5f7fa; padding: 15px; border-radius: 5px; word-break: break-all;">
            {verification_url}
        </p>

        <p><strong>Este link expira em 24 horas.</strong></p>

        <p>Após verificar sua conta, você terá acesso a:</p>
        <ul>
            <li>✅ Leads qualificados (clientes que já pagaram R$ 7)</li>
            <li>✅ Dashboard com métricas em tempo real</li>
            <li>✅ Integração com tribunais (PJe, eProc)</li>
            <li>✅ Monitoramento de prazos</li>
            <li>✅ Perfil público com SEO</li>
        </ul>

        <p>Estamos felizes em tê-lo conosco!</p>
        <p><strong>Equipe Doutora IA</strong></p>
        """

        base_template = Template(self._get_base_template())
        html = base_template.render(
            title="Verifique sua conta",
            content=content
        )

        return self._send_email(
            to_email=to_email,
            subject="Verifique sua conta - Doutora IA",
            html_body=html,
            text_body=f"Olá {lawyer_name}, clique no link para verificar sua conta: {verification_url}"
        )

    def send_password_reset_email(self, to_email: str, lawyer_name: str, token: str) -> bool:
        """
        Envia email de reset de senha

        Args:
            to_email: Email do advogado
            lawyer_name: Nome do advogado
            token: Token de reset

        Returns:
            True se enviado com sucesso
        """
        base_url = os.getenv("BASE_URL", "http://localhost:3000")
        reset_url = f"{base_url}/reset-password.html?token={token}"

        content = f"""
        <h2 style="color: #1a5490;">Redefinição de Senha</h2>

        <p>Olá {lawyer_name},</p>

        <p>Recebemos uma solicitação para redefinir a senha da sua conta na Doutora IA.</p>

        <p>Se foi você quem solicitou, clique no botão abaixo para criar uma nova senha:</p>

        <p style="text-align: center;">
            <a href="{reset_url}" class="button">Redefinir Minha Senha</a>
        </p>

        <p>Ou copie e cole este link no seu navegador:</p>
        <p style="background: #f5f7fa; padding: 15px; border-radius: 5px; word-break: break-all;">
            {reset_url}
        </p>

        <p><strong>Este link expira em 1 hora.</strong></p>

        <div style="background: #fff3cd; border-left: 4px solid #ffc107; padding: 15px; margin: 20px 0;">
            <strong>⚠️ Importante:</strong><br>
            Se você não solicitou esta alteração, ignore este email. Sua senha permanecerá a mesma.
        </div>

        <p>Por segurança, nunca compartilhe este link com ninguém.</p>

        <p><strong>Equipe Doutora IA</strong></p>
        """

        base_template = Template(self._get_base_template())
        html = base_template.render(
            title="Redefinir senha",
            content=content
        )

        return self._send_email(
            to_email=to_email,
            subject="Redefinir sua senha - Doutora IA",
            html_body=html,
            text_body=f"Olá {lawyer_name}, clique no link para redefinir sua senha: {reset_url}"
        )

    def send_welcome_email(self, to_email: str, lawyer_name: str) -> bool:
        """
        Envia email de boas-vindas após verificação

        Args:
            to_email: Email do advogado
            lawyer_name: Nome do advogado

        Returns:
            True se enviado com sucesso
        """
        content = f"""
        <h2 style="color: #1a5490;">Conta verificada com sucesso! 🎉</h2>

        <p>Olá {lawyer_name},</p>

        <p>Sua conta foi verificada com sucesso! Agora você tem acesso completo à plataforma Doutora IA.</p>

        <h3>Próximos Passos:</h3>

        <ol>
            <li><strong>Complete seu perfil</strong>
                <p>Adicione sua foto, biografia e áreas de atuação para aumentar sua visibilidade.</p>
            </li>

            <li><strong>Ative seu perfil público</strong>
                <p>Seu perfil SEO-otimizado pode trazer leads orgânicos gratuitos do Google.</p>
            </li>

            <li><strong>Explore o dashboard</strong>
                <p>Veja métricas, gráficos e gerencie seus leads de forma eficiente.</p>
            </li>

            <li><strong>Comece a receber leads</strong>
                <p>Leads qualificados (clientes que já pagaram R$ 7) chegam automaticamente para você.</p>
            </li>
        </ol>

        <p style="text-align: center;">
            <a href="http://localhost:3000/dashboard.html" class="button">Acessar Dashboard</a>
        </p>

        <div style="background: #e7f3ff; border-left: 4px solid #1a5490; padding: 15px; margin: 20px 0;">
            <strong>💡 Dica:</strong><br>
            Advogados que respondem leads em até 4 horas têm taxa de conversão 3x maior!
        </div>

        <p>Qualquer dúvida, estamos à disposição.</p>

        <p><strong>Sucesso na sua jornada!</strong><br>
        Equipe Doutora IA</p>
        """

        base_template = Template(self._get_base_template())
        html = base_template.render(
            title="Bem-vindo à Doutora IA",
            content=content
        )

        return self._send_email(
            to_email=to_email,
            subject="Bem-vindo à Doutora IA! 🎉",
            html_body=html,
            text_body=f"Olá {lawyer_name}, sua conta foi verificada! Acesse: http://localhost:3000/dashboard.html"
        )

    def send_new_lead_notification(
        self,
        to_email: str,
        lawyer_name: str,
        lead_area: str,
        lead_description: str,
        lead_value: float
    ) -> bool:
        """
        Envia notificação de novo lead disponível

        Args:
            to_email: Email do advogado
            lawyer_name: Nome do advogado
            lead_area: Área do lead
            lead_description: Descrição resumida
            lead_value: Valor estimado de honorários

        Returns:
            True se enviado com sucesso
        """
        content = f"""
        <h2 style="color: #28a745;">🎯 Novo Lead Qualificado Disponível!</h2>

        <p>Olá {lawyer_name},</p>

        <p>Um novo lead qualificado está disponível para você:</p>

        <div style="background: #f8f9fa; border-radius: 5px; padding: 20px; margin: 20px 0;">
            <p><strong>Área:</strong> {lead_area.upper()}</p>
            <p><strong>Descrição:</strong> {lead_description}</p>
            <p><strong>Honorários Estimados:</strong> <span style="color: #28a745; font-size: 1.3rem; font-weight: bold;">R$ {lead_value:,.2f}</span></p>
        </div>

        <div style="background: #fff3e0; border-left: 4px solid #ffc107; padding: 15px; margin: 20px 0;">
            <strong>⏰ Atenção:</strong><br>
            Este lead tem janela de exclusividade de 48 horas. Aceite logo para garantir!
        </div>

        <p style="text-align: center;">
            <a href="http://localhost:3000/leads.html" class="button">Ver Lead Agora</a>
        </p>

        <p><strong>O cliente já pagou R$ 7 pelo relatório</strong>, indicando interesse real em contratar um advogado.</p>

        <p>Boa sorte!</p>
        <p><strong>Equipe Doutora IA</strong></p>
        """

        base_template = Template(self._get_base_template())
        html = base_template.render(
            title="Novo Lead Disponível",
            content=content
        )

        return self._send_email(
            to_email=to_email,
            subject=f"🎯 Novo Lead: {lead_area.upper()} - R$ {lead_value:,.0f}",
            html_body=html,
            text_body=f"Novo lead de {lead_area} disponível. Valor estimado: R$ {lead_value:,.2f}. Acesse: http://localhost:3000/leads.html"
        )


# Instância global
email_service = EmailService()

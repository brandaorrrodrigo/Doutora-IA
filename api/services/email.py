"""
Email Service for Doutora IA
Professional email notifications using Resend (or SMTP fallback)
"""

import os
import logging
from typing import Dict, List, Optional
from datetime import datetime
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import httpx

logger = logging.getLogger(__name__)


class EmailService:
    """
    Multi-provider email service with beautiful HTML templates
    Supports: Resend (preferred), SMTP (fallback), Console (dev)
    """

    def __init__(self):
        self.provider = os.getenv("EMAIL_PROVIDER", "console")  # resend | smtp | console
        self.from_email = os.getenv("EMAIL_FROM", "noreply@doutora-ia.com")
        self.from_name = os.getenv("EMAIL_FROM_NAME", "Doutora IA")

        # Resend configuration
        self.resend_api_key = os.getenv("RESEND_API_KEY", "")

        # SMTP configuration
        self.smtp_host = os.getenv("SMTP_HOST", "")
        self.smtp_port = int(os.getenv("SMTP_PORT", "587"))
        self.smtp_user = os.getenv("SMTP_USER", "")
        self.smtp_password = os.getenv("SMTP_PASSWORD", "")

        logger.info(f"Email service initialized: provider={self.provider}")

    def send_email(
        self,
        to_email: str,
        subject: str,
        html_body: str,
        text_body: Optional[str] = None,
        reply_to: Optional[str] = None
    ) -> bool:
        """
        Send email using configured provider
        Returns True if successful, False otherwise
        """
        try:
            if self.provider == "resend":
                return self._send_via_resend(to_email, subject, html_body, text_body, reply_to)
            elif self.provider == "smtp":
                return self._send_via_smtp(to_email, subject, html_body, text_body)
            else:  # console mode for development
                return self._send_via_console(to_email, subject, html_body, text_body)
        except Exception as e:
            logger.error(f"Email send failed to {to_email}: {e}")
            return False

    def _send_via_resend(
        self,
        to_email: str,
        subject: str,
        html_body: str,
        text_body: Optional[str],
        reply_to: Optional[str]
    ) -> bool:
        """Send email via Resend API"""
        if not self.resend_api_key:
            logger.error("Resend API key not configured")
            return False

        try:
            payload = {
                "from": f"{self.from_name} <{self.from_email}>",
                "to": [to_email],
                "subject": subject,
                "html": html_body,
            }

            if text_body:
                payload["text"] = text_body

            if reply_to:
                payload["reply_to"] = reply_to

            response = httpx.post(
                "https://api.resend.com/emails",
                headers={
                    "Authorization": f"Bearer {self.resend_api_key}",
                    "Content-Type": "application/json"
                },
                json=payload,
                timeout=10
            )

            if response.status_code == 200:
                logger.info(f"✓ Email sent via Resend to {to_email}: {subject}")
                return True
            else:
                logger.error(f"Resend API error: {response.status_code} - {response.text}")
                return False

        except Exception as e:
            logger.error(f"Resend send error: {e}")
            return False

    def _send_via_smtp(
        self,
        to_email: str,
        subject: str,
        html_body: str,
        text_body: Optional[str]
    ) -> bool:
        """Send email via SMTP"""
        if not all([self.smtp_host, self.smtp_user, self.smtp_password]):
            logger.error("SMTP not fully configured")
            return False

        try:
            msg = MIMEMultipart("alternative")
            msg["From"] = f"{self.from_name} <{self.from_email}>"
            msg["To"] = to_email
            msg["Subject"] = subject

            if text_body:
                msg.attach(MIMEText(text_body, "plain"))
            msg.attach(MIMEText(html_body, "html"))

            with smtplib.SMTP(self.smtp_host, self.smtp_port) as server:
                server.starttls()
                server.login(self.smtp_user, self.smtp_password)
                server.send_message(msg)

            logger.info(f"✓ Email sent via SMTP to {to_email}: {subject}")
            return True

        except Exception as e:
            logger.error(f"SMTP send error: {e}")
            return False

    def _send_via_console(
        self,
        to_email: str,
        subject: str,
        html_body: str,
        text_body: Optional[str]
    ) -> bool:
        """Development mode - log email to console"""
        logger.info(f"""
        ╔════════════════════════════════════════════════════════════
        ║ 📧 EMAIL (Console Mode - Development)
        ╠════════════════════════════════════════════════════════════
        ║ To: {to_email}
        ║ Subject: {subject}
        ╠════════════════════════════════════════════════════════════
        ║ {text_body or 'HTML email (check browser for preview)'}
        ╚════════════════════════════════════════════════════════════
        """)
        return True

    # ========================================
    # TEMPLATE METHODS - Specific email types
    # ========================================

    def send_welcome_email(self, to_email: str, user_name: str) -> bool:
        """Welcome email for new users"""
        subject = "Bem-vindo à Doutora IA! 🎉"

        html_body = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
        </head>
        <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333; max-width: 600px; margin: 0 auto; padding: 20px;">
            <div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 30px; text-align: center; border-radius: 10px 10px 0 0;">
                <h1 style="margin: 0; font-size: 28px;">⚖️ Doutora IA</h1>
                <p style="margin: 10px 0 0 0; font-size: 16px;">Inteligência Artificial Jurídica</p>
            </div>

            <div style="background: #f9f9f9; padding: 30px; border-radius: 0 0 10px 10px;">
                <h2 style="color: #667eea; margin-top: 0;">Olá, {user_name}! 👋</h2>

                <p>Seja muito bem-vindo à <strong>Doutora IA</strong> - sua assistente jurídica inteligente!</p>

                <p>Agora você tem acesso a:</p>

                <ul style="background: white; padding: 20px 20px 20px 40px; border-left: 4px solid #667eea; border-radius: 5px;">
                    <li><strong>Análise de Casos</strong>: Obtenha análises jurídicas detalhadas em segundos</li>
                    <li><strong>Pesquisa RAG</strong>: Busque em nossa base de jurisprudência e legislação</li>
                    <li><strong>Relatórios PDF</strong>: Gere documentos profissionais automaticamente</li>
                    <li><strong>Redação Automática</strong>: Crie petições e documentos jurídicos</li>
                </ul>

                <div style="text-align: center; margin: 30px 0;">
                    <a href="https://doutora-ia.com/dashboard" style="display: inline-block; background: #667eea; color: white; padding: 15px 30px; text-decoration: none; border-radius: 5px; font-weight: bold;">
                        Começar Agora
                    </a>
                </div>

                <p style="font-size: 14px; color: #666; margin-top: 30px;">
                    <strong>Dica:</strong> Comece fazendo uma análise de caso para conhecer o poder da plataforma!
                </p>

                <hr style="border: none; border-top: 1px solid #ddd; margin: 30px 0;">

                <p style="font-size: 12px; color: #999; text-align: center;">
                    Dúvidas? Responda este email ou acesse nossa central de ajuda.<br>
                    © {datetime.now().year} Doutora IA. Todos os direitos reservados.
                </p>
            </div>
        </body>
        </html>
        """

        text_body = f"""
        Olá, {user_name}!

        Seja muito bem-vindo à Doutora IA - sua assistente jurídica inteligente!

        Agora você tem acesso a:
        - Análise de Casos: Obtenha análises jurídicas detalhadas em segundos
        - Pesquisa RAG: Busque em nossa base de jurisprudência e legislação
        - Relatórios PDF: Gere documentos profissionais automaticamente
        - Redação Automática: Crie petições e documentos jurídicos

        Acesse: https://doutora-ia.com/dashboard

        Dúvidas? Responda este email!

        © {datetime.now().year} Doutora IA
        """

        return self.send_email(to_email, subject, html_body, text_body)

    def send_analysis_complete_email(
        self,
        to_email: str,
        user_name: str,
        case_description: str,
        analysis_summary: str
    ) -> bool:
        """Notification when case analysis is complete"""
        subject = "✅ Sua análise está pronta!"

        # Truncate for email display
        description_preview = case_description[:200] + "..." if len(case_description) > 200 else case_description
        summary_preview = analysis_summary[:300] + "..." if len(analysis_summary) > 300 else analysis_summary

        html_body = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
        </head>
        <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333; max-width: 600px; margin: 0 auto; padding: 20px;">
            <div style="background: linear-gradient(135deg, #11998e 0%, #38ef7d 100%); color: white; padding: 30px; text-align: center; border-radius: 10px 10px 0 0;">
                <h1 style="margin: 0; font-size: 28px;">✅ Análise Concluída!</h1>
            </div>

            <div style="background: #f9f9f9; padding: 30px; border-radius: 0 0 10px 10px;">
                <h2 style="color: #11998e; margin-top: 0;">Olá, {user_name}!</h2>

                <p>Sua análise jurídica foi concluída com sucesso! 🎉</p>

                <div style="background: white; padding: 20px; border-left: 4px solid #11998e; border-radius: 5px; margin: 20px 0;">
                    <h3 style="margin-top: 0; color: #333; font-size: 16px;">Caso analisado:</h3>
                    <p style="color: #666; font-style: italic;">{description_preview}</p>
                </div>

                <div style="background: #e8f5e9; padding: 20px; border-radius: 5px; margin: 20px 0;">
                    <h3 style="margin-top: 0; color: #333; font-size: 16px;">Resumo da análise:</h3>
                    <p style="color: #555;">{summary_preview}</p>
                </div>

                <div style="text-align: center; margin: 30px 0;">
                    <a href="https://doutora-ia.com/dashboard" style="display: inline-block; background: #11998e; color: white; padding: 15px 30px; text-decoration: none; border-radius: 5px; font-weight: bold;">
                        Ver Análise Completa
                    </a>
                </div>

                <p style="font-size: 14px; color: #666; margin-top: 30px;">
                    <strong>Próximos passos:</strong><br>
                    • Revise a análise detalhada no dashboard<br>
                    • Gere um relatório PDF profissional<br>
                    • Use a redação automática para criar petições
                </p>

                <hr style="border: none; border-top: 1px solid #ddd; margin: 30px 0;">

                <p style="font-size: 12px; color: #999; text-align: center;">
                    © {datetime.now().year} Doutora IA. Todos os direitos reservados.
                </p>
            </div>
        </body>
        </html>
        """

        text_body = f"""
        Olá, {user_name}!

        Sua análise jurídica foi concluída com sucesso!

        Caso analisado:
        {description_preview}

        Resumo:
        {summary_preview}

        Acesse o dashboard para ver a análise completa:
        https://doutora-ia.com/dashboard

        © {datetime.now().year} Doutora IA
        """

        return self.send_email(to_email, subject, html_body, text_body)

    def send_payment_confirmation_email(
        self,
        to_email: str,
        user_name: str,
        amount: float,
        product_name: str,
        payment_id: str
    ) -> bool:
        """Payment confirmation email"""
        subject = f"💳 Pagamento Confirmado - {product_name}"

        html_body = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
        </head>
        <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333; max-width: 600px; margin: 0 auto; padding: 20px;">
            <div style="background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%); color: white; padding: 30px; text-align: center; border-radius: 10px 10px 0 0;">
                <h1 style="margin: 0; font-size: 28px;">💳 Pagamento Confirmado!</h1>
            </div>

            <div style="background: #f9f9f9; padding: 30px; border-radius: 0 0 10px 10px;">
                <h2 style="color: #f5576c; margin-top: 0;">Olá, {user_name}!</h2>

                <p>Recebemos seu pagamento com sucesso! 🎉</p>

                <div style="background: white; padding: 20px; border-radius: 5px; margin: 20px 0;">
                    <table style="width: 100%; border-collapse: collapse;">
                        <tr>
                            <td style="padding: 10px 0; border-bottom: 1px solid #eee;"><strong>Produto:</strong></td>
                            <td style="padding: 10px 0; border-bottom: 1px solid #eee; text-align: right;">{product_name}</td>
                        </tr>
                        <tr>
                            <td style="padding: 10px 0; border-bottom: 1px solid #eee;"><strong>Valor:</strong></td>
                            <td style="padding: 10px 0; border-bottom: 1px solid #eee; text-align: right;">R$ {amount/100:.2f}</td>
                        </tr>
                        <tr>
                            <td style="padding: 10px 0; border-bottom: 1px solid #eee;"><strong>ID do Pagamento:</strong></td>
                            <td style="padding: 10px 0; border-bottom: 1px solid #eee; text-align: right; font-family: monospace; font-size: 12px;">{payment_id}</td>
                        </tr>
                        <tr>
                            <td style="padding: 10px 0;"><strong>Data:</strong></td>
                            <td style="padding: 10px 0; text-align: right;">{datetime.now().strftime('%d/%m/%Y %H:%M')}</td>
                        </tr>
                    </table>
                </div>

                <div style="background: #e8f5e9; padding: 15px; border-radius: 5px; margin: 20px 0;">
                    <p style="margin: 0; color: #2e7d32;">
                        ✓ Seu conteúdo já está disponível no dashboard!
                    </p>
                </div>

                <div style="text-align: center; margin: 30px 0;">
                    <a href="https://doutora-ia.com/dashboard" style="display: inline-block; background: #f5576c; color: white; padding: 15px 30px; text-decoration: none; border-radius: 5px; font-weight: bold;">
                        Acessar Conteúdo
                    </a>
                </div>

                <hr style="border: none; border-top: 1px solid #ddd; margin: 30px 0;">

                <p style="font-size: 12px; color: #999; text-align: center;">
                    Guarde este email como comprovante de pagamento.<br>
                    © {datetime.now().year} Doutora IA. Todos os direitos reservados.
                </p>
            </div>
        </body>
        </html>
        """

        text_body = f"""
        Olá, {user_name}!

        Recebemos seu pagamento com sucesso!

        Detalhes:
        - Produto: {product_name}
        - Valor: R$ {amount/100:.2f}
        - ID do Pagamento: {payment_id}
        - Data: {datetime.now().strftime('%d/%m/%Y %H:%M')}

        Seu conteúdo já está disponível no dashboard:
        https://doutora-ia.com/dashboard

        Guarde este email como comprovante.

        © {datetime.now().year} Doutora IA
        """

        return self.send_email(to_email, subject, html_body, text_body)

    def send_new_lead_email(
        self,
        to_email: str,
        lawyer_name: str,
        case_description: str,
        client_contact: str,
        case_area: str,
        exclusivity_hours: int = 48
    ) -> bool:
        """New lead notification for lawyers"""
        subject = f"🎯 Novo Lead: {case_area}"

        html_body = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
        </head>
        <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333; max-width: 600px; margin: 0 auto; padding: 20px;">
            <div style="background: linear-gradient(135deg, #fa709a 0%, #fee140 100%); color: white; padding: 30px; text-align: center; border-radius: 10px 10px 0 0;">
                <h1 style="margin: 0; font-size: 28px;">🎯 Novo Lead!</h1>
                <p style="margin: 10px 0 0 0; font-size: 16px;">Exclusividade de {exclusivity_hours}h</p>
            </div>

            <div style="background: #f9f9f9; padding: 30px; border-radius: 0 0 10px 10px;">
                <h2 style="color: #fa709a; margin-top: 0;">Olá, Dr(a). {lawyer_name}!</h2>

                <p>Um novo cliente precisa de seus serviços! 🎉</p>

                <div style="background: white; padding: 20px; border-left: 4px solid #fa709a; border-radius: 5px; margin: 20px 0;">
                    <h3 style="margin-top: 0; color: #333; font-size: 16px;">Área:</h3>
                    <p style="color: #fa709a; font-weight: bold; font-size: 18px; margin: 5px 0;">{case_area}</p>
                </div>

                <div style="background: #fff9e6; padding: 20px; border-radius: 5px; margin: 20px 0;">
                    <h3 style="margin-top: 0; color: #333; font-size: 16px;">Descrição do Caso:</h3>
                    <p style="color: #555;">{case_description}</p>
                </div>

                <div style="background: #e3f2fd; padding: 20px; border-radius: 5px; margin: 20px 0;">
                    <h3 style="margin-top: 0; color: #333; font-size: 16px;">Contato do Cliente:</h3>
                    <p style="color: #1976d2; font-weight: bold; margin: 5px 0;">{client_contact}</p>
                </div>

                <div style="background: #fff3e0; padding: 15px; border-radius: 5px; margin: 20px 0; border: 2px dashed #ff9800;">
                    <p style="margin: 0; color: #e65100; font-weight: bold;">
                        ⏰ Este lead é exclusivo seu por {exclusivity_hours} horas!
                    </p>
                </div>

                <div style="text-align: center; margin: 30px 0;">
                    <a href="https://doutora-ia.com/lawyer/leads" style="display: inline-block; background: #fa709a; color: white; padding: 15px 30px; text-decoration: none; border-radius: 5px; font-weight: bold;">
                        Ver Detalhes Completos
                    </a>
                </div>

                <p style="font-size: 14px; color: #666; margin-top: 30px;">
                    <strong>Dica:</strong> Entre em contato rapidamente para aumentar suas chances de conversão!
                </p>

                <hr style="border: none; border-top: 1px solid #ddd; margin: 30px 0;">

                <p style="font-size: 12px; color: #999; text-align: center;">
                    © {datetime.now().year} Doutora IA - Marketplace Jurídico
                </p>
            </div>
        </body>
        </html>
        """

        text_body = f"""
        Olá, Dr(a). {lawyer_name}!

        Um novo cliente precisa de seus serviços!

        Área: {case_area}

        Descrição do Caso:
        {case_description}

        Contato do Cliente:
        {client_contact}

        ⏰ Este lead é exclusivo seu por {exclusivity_hours} horas!

        Acesse: https://doutora-ia.com/lawyer/leads

        Dica: Entre em contato rapidamente para aumentar suas chances de conversão!

        © {datetime.now().year} Doutora IA
        """

        return self.send_email(to_email, subject, html_body, text_body)

    def send_weekly_report_email(
        self,
        to_email: str,
        user_name: str,
        stats: Dict[str, int]
    ) -> bool:
        """Weekly activity report"""
        subject = f"📊 Seu Relatório Semanal - Doutora IA"

        total_analyses = stats.get("analyses", 0)
        total_searches = stats.get("searches", 0)
        total_reports = stats.get("reports", 0)
        total_documents = stats.get("documents", 0)

        html_body = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
        </head>
        <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333; max-width: 600px; margin: 0 auto; padding: 20px;">
            <div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 30px; text-align: center; border-radius: 10px 10px 0 0;">
                <h1 style="margin: 0; font-size: 28px;">📊 Relatório Semanal</h1>
                <p style="margin: 10px 0 0 0; font-size: 14px;">Semana de {(datetime.now()).strftime('%d/%m/%Y')}</p>
            </div>

            <div style="background: #f9f9f9; padding: 30px; border-radius: 0 0 10px 10px;">
                <h2 style="color: #667eea; margin-top: 0;">Olá, {user_name}! 👋</h2>

                <p>Aqui está um resumo da sua atividade esta semana:</p>

                <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 15px; margin: 30px 0;">
                    <div style="background: white; padding: 20px; border-radius: 10px; text-align: center; box-shadow: 0 2px 5px rgba(0,0,0,0.1);">
                        <div style="font-size: 32px; color: #667eea; font-weight: bold;">{total_analyses}</div>
                        <div style="color: #666; font-size: 14px; margin-top: 5px;">Análises</div>
                    </div>
                    <div style="background: white; padding: 20px; border-radius: 10px; text-align: center; box-shadow: 0 2px 5px rgba(0,0,0,0.1);">
                        <div style="font-size: 32px; color: #11998e; font-weight: bold;">{total_searches}</div>
                        <div style="color: #666; font-size: 14px; margin-top: 5px;">Pesquisas</div>
                    </div>
                    <div style="background: white; padding: 20px; border-radius: 10px; text-align: center; box-shadow: 0 2px 5px rgba(0,0,0,0.1);">
                        <div style="font-size: 32px; color: #f5576c; font-weight: bold;">{total_reports}</div>
                        <div style="color: #666; font-size: 14px; margin-top: 5px;">Relatórios</div>
                    </div>
                    <div style="background: white; padding: 20px; border-radius: 10px; text-align: center; box-shadow: 0 2px 5px rgba(0,0,0,0.1);">
                        <div style="font-size: 32px; color: #fa709a; font-weight: bold;">{total_documents}</div>
                        <div style="color: #666; font-size: 14px; margin-top: 5px;">Documentos</div>
                    </div>
                </div>

                <div style="background: #e8f5e9; padding: 20px; border-radius: 5px; margin: 20px 0;">
                    <p style="margin: 0; color: #2e7d32; font-weight: bold;">
                        🎉 Ótimo trabalho esta semana!
                    </p>
                </div>

                <div style="text-align: center; margin: 30px 0;">
                    <a href="https://doutora-ia.com/dashboard" style="display: inline-block; background: #667eea; color: white; padding: 15px 30px; text-decoration: none; border-radius: 5px; font-weight: bold;">
                        Acessar Dashboard
                    </a>
                </div>

                <hr style="border: none; border-top: 1px solid #ddd; margin: 30px 0;">

                <p style="font-size: 12px; color: #999; text-align: center;">
                    Você recebe este email semanalmente. Para alterar preferências, acesse as configurações.<br>
                    © {datetime.now().year} Doutora IA. Todos os direitos reservados.
                </p>
            </div>
        </body>
        </html>
        """

        text_body = f"""
        Olá, {user_name}!

        Aqui está um resumo da sua atividade esta semana:

        📊 Estatísticas:
        - Análises realizadas: {total_analyses}
        - Pesquisas feitas: {total_searches}
        - Relatórios gerados: {total_reports}
        - Documentos criados: {total_documents}

        Ótimo trabalho esta semana!

        Acesse: https://doutora-ia.com/dashboard

        © {datetime.now().year} Doutora IA
        """

        return self.send_email(to_email, subject, html_body, text_body)


# Global instance
email_service = EmailService()

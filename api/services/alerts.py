"""
Sistema de alertas de prazos processuais
WhatsApp, Email, SMS
"""
import os
from datetime import datetime, timedelta
from typing import List, Dict
from sqlalchemy.orm import Session
from twilio.rest import Client
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart


class AlertSystem:
    """Sistema de alertas multi-canal"""

    def __init__(self):
        # Twilio (WhatsApp + SMS)
        self.twilio_sid = os.getenv("TWILIO_ACCOUNT_SID")
        self.twilio_token = os.getenv("TWILIO_AUTH_TOKEN")
        self.twilio_whatsapp = os.getenv("TWILIO_WHATSAPP_NUMBER", "whatsapp:+14155238886")
        self.twilio_phone = os.getenv("TWILIO_PHONE_NUMBER")

        if self.twilio_sid and self.twilio_token:
            self.twilio_client = Client(self.twilio_sid, self.twilio_token)
        else:
            self.twilio_client = None

        # Email (SMTP)
        self.smtp_host = os.getenv("SMTP_HOST", "smtp.gmail.com")
        self.smtp_port = int(os.getenv("SMTP_PORT", "587"))
        self.smtp_user = os.getenv("SMTP_USER")
        self.smtp_pass = os.getenv("SMTP_PASS")
        self.from_email = os.getenv("FROM_EMAIL", "noreply@doutoraia.com.br")

    def enviar_whatsapp(self, to: str, message: str) -> bool:
        """
        Envia mensagem via WhatsApp (Twilio)

        Args:
            to: Número de telefone com código do país (+5511999999999)
            message: Texto da mensagem

        Returns:
            True se enviado com sucesso
        """
        if not self.twilio_client:
            print("Twilio não configurado")
            return False

        try:
            # Garantir formato WhatsApp
            if not to.startswith("whatsapp:"):
                to = f"whatsapp:{to}"

            message_obj = self.twilio_client.messages.create(
                from_=self.twilio_whatsapp,
                to=to,
                body=message
            )

            print(f"✓ WhatsApp enviado: {message_obj.sid}")
            return True

        except Exception as e:
            print(f"✗ Erro ao enviar WhatsApp: {e}")
            return False

    def enviar_sms(self, to: str, message: str) -> bool:
        """
        Envia SMS (Twilio)

        Args:
            to: Número de telefone
            message: Texto (máx 160 caracteres)

        Returns:
            True se enviado
        """
        if not self.twilio_client:
            print("Twilio não configurado")
            return False

        try:
            message_obj = self.twilio_client.messages.create(
                from_=self.twilio_phone,
                to=to,
                body=message[:160]  # Limitar a 160 chars
            )

            print(f"✓ SMS enviado: {message_obj.sid}")
            return True

        except Exception as e:
            print(f"✗ Erro ao enviar SMS: {e}")
            return False

    def enviar_email(self, to: str, subject: str, body: str, html: bool = False) -> bool:
        """
        Envia email via SMTP

        Args:
            to: Email destinatário
            subject: Assunto
            body: Corpo do email
            html: Se True, envia como HTML

        Returns:
            True se enviado
        """
        if not self.smtp_user or not self.smtp_pass:
            print("SMTP não configurado")
            return False

        try:
            msg = MIMEMultipart('alternative')
            msg['From'] = self.from_email
            msg['To'] = to
            msg['Subject'] = subject

            if html:
                msg.attach(MIMEText(body, 'html', 'utf-8'))
            else:
                msg.attach(MIMEText(body, 'plain', 'utf-8'))

            with smtplib.SMTP(self.smtp_host, self.smtp_port) as server:
                server.starttls()
                server.login(self.smtp_user, self.smtp_pass)
                server.send_message(msg)

            print(f"✓ Email enviado para {to}")
            return True

        except Exception as e:
            print(f"✗ Erro ao enviar email: {e}")
            return False

    def alertar_prazo(
        self,
        advogado_nome: str,
        advogado_phone: str,
        advogado_email: str,
        processo_numero: str,
        prazo_tipo: str,
        prazo_data: str,
        dias_restantes: int
    ):
        """
        Envia alerta de prazo por todos os canais configurados

        Args:
            advogado_nome: Nome do advogado
            advogado_phone: Telefone (WhatsApp/SMS)
            advogado_email: Email
            processo_numero: Número do processo
            prazo_tipo: Tipo do prazo (recurso, contestação, etc)
            prazo_data: Data limite (YYYY-MM-DD)
            dias_restantes: Dias até o vencimento
        """

        # Mensagem base
        urgencia = "🔴 URGENTE" if dias_restantes <= 2 else "⚠️ ATENÇÃO"

        mensagem = f"""
{urgencia} - Prazo Processual

Dr(a). {advogado_nome},

Processo: {processo_numero}
Prazo: {prazo_tipo}
Vencimento: {prazo_data}
Faltam: {dias_restantes} dia(s)

Acesse: doutoraia.com.br/processos

Doutora IA
        """.strip()

        # Email HTML
        email_html = f"""
        <html>
        <body style="font-family: Arial, sans-serif; padding: 20px;">
            <div style="background: {'#ff0000' if dias_restantes <= 2 else '#ffa500'}; color: white; padding: 15px; border-radius: 5px;">
                <h2>{urgencia} - Prazo Processual</h2>
            </div>

            <div style="margin-top: 20px;">
                <p>Dr(a). {advogado_nome},</p>

                <table style="width: 100%; border-collapse: collapse; margin: 20px 0;">
                    <tr style="background: #f5f5f5;">
                        <td style="padding: 10px; border: 1px solid #ddd;"><strong>Processo:</strong></td>
                        <td style="padding: 10px; border: 1px solid #ddd;">{processo_numero}</td>
                    </tr>
                    <tr>
                        <td style="padding: 10px; border: 1px solid #ddd;"><strong>Tipo de Prazo:</strong></td>
                        <td style="padding: 10px; border: 1px solid #ddd;">{prazo_tipo}</td>
                    </tr>
                    <tr style="background: #f5f5f5;">
                        <td style="padding: 10px; border: 1px solid #ddd;"><strong>Data Limite:</strong></td>
                        <td style="padding: 10px; border: 1px solid #ddd;">{prazo_data}</td>
                    </tr>
                    <tr>
                        <td style="padding: 10px; border: 1px solid #ddd;"><strong>Dias Restantes:</strong></td>
                        <td style="padding: 10px; border: 1px solid #ddd; font-size: 20px; font-weight: bold; color: {'red' if dias_restantes <= 2 else 'orange'};">
                            {dias_restantes} dia(s)
                        </td>
                    </tr>
                </table>

                <a href="https://doutoraia.com.br/processos/{processo_numero}"
                   style="display: inline-block; background: #1a5490; color: white; padding: 15px 30px;
                          text-decoration: none; border-radius: 5px; margin: 20px 0;">
                    Acessar Processo
                </a>

                <p style="margin-top: 30px; color: #666; font-size: 12px;">
                    Doutora IA - Seu assistente jurídico inteligente<br>
                    www.doutoraia.com.br
                </p>
            </div>
        </body>
        </html>
        """

        # Enviar por todos os canais
        resultados = {}

        if advogado_phone:
            # WhatsApp (prioridade)
            resultados['whatsapp'] = self.enviar_whatsapp(advogado_phone, mensagem)

            # SMS (fallback se WhatsApp falhar)
            if not resultados['whatsapp']:
                resultados['sms'] = self.enviar_sms(advogado_phone, mensagem)

        if advogado_email:
            resultados['email'] = self.enviar_email(
                advogado_email,
                f"{urgencia} - Prazo {prazo_tipo} - {processo_numero}",
                email_html,
                html=True
            )

        return resultados


class PrazoMonitor:
    """Monitor automático de prazos processuais"""

    def __init__(self, db: Session):
        self.db = db
        self.alert_system = AlertSystem()

    def verificar_prazos_pendentes(self):
        """
        Verifica todos os prazos e envia alertas

        Deve ser executado diariamente pelo worker
        """
        from models import Processo, Prazo, Lawyer

        hoje = datetime.now().date()

        # Buscar prazos próximos do vencimento
        prazos = self.db.query(Prazo).filter(
            Prazo.data_limite >= hoje,
            Prazo.data_limite <= hoje + timedelta(days=5),
            Prazo.alertado == False
        ).all()

        for prazo in prazos:
            dias_restantes = (prazo.data_limite - hoje).days

            # Alertar em:
            # - 5 dias antes
            # - 3 dias antes
            # - 1 dia antes
            # - No dia
            if dias_restantes in [5, 3, 1, 0]:
                processo = prazo.processo
                advogado = processo.advogado

                if advogado:
                    self.alert_system.alertar_prazo(
                        advogado_nome=advogado.name,
                        advogado_phone=advogado.phone,
                        advogado_email=advogado.email,
                        processo_numero=processo.numero,
                        prazo_tipo=prazo.tipo,
                        prazo_data=prazo.data_limite.strftime("%d/%m/%Y"),
                        dias_restantes=dias_restantes
                    )

                    # Marcar como alertado (evitar duplicatas)
                    if dias_restantes == 0:
                        prazo.alertado = True

        self.db.commit()

        print(f"✓ Verificação de prazos concluída: {len(prazos)} prazos processados")


# Singleton
_alert_system = None


def get_alert_system() -> AlertSystem:
    global _alert_system
    if _alert_system is None:
        _alert_system = AlertSystem()
    return _alert_system

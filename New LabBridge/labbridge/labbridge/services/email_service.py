"""
Email Service - Serviço de envio de emails
LabBridge

Suporta múltiplos providers:
- SMTP (Gmail, Outlook, etc)
- Resend
- SendGrid
"""
import os
from typing import Dict, Any, Optional, Tuple, List
from datetime import datetime
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import smtplib
import ssl


class EmailService:
    """Serviço de envio de emails"""
    
    def __init__(self):
        # Configurações SMTP
        self.smtp_host = os.getenv("SMTP_HOST", "smtp.gmail.com")
        self.smtp_port = int(os.getenv("SMTP_PORT", "587"))
        self.smtp_user = os.getenv("SMTP_USER", "")
        self.smtp_password = os.getenv("SMTP_PASSWORD", "")
        self.from_email = os.getenv("EMAIL_FROM", "noreply@labbridge.com.br")
        self.from_name = os.getenv("EMAIL_FROM_NAME", "LabBridge")
        
        # Provider alternativo (Resend)
        self.resend_api_key = os.getenv("RESEND_API_KEY", "")
        
        # Templates base
        self.app_url = os.getenv("APP_URL", "http://localhost:3000")
    
    @property
    def is_configured(self) -> bool:
        """Verifica se algum provider está configurado"""
        return bool(self.smtp_user and self.smtp_password) or bool(self.resend_api_key)
    
    def _get_html_template(self, title: str, content: str, button_text: str = None, button_url: str = None) -> str:
        """Gera template HTML para email"""
        button_html = ""
        if button_text and button_url:
            button_html = f'''
            <div style="text-align: center; margin: 30px 0;">
                <a href="{button_url}" 
                   style="background-color: #2563EB; color: white; padding: 14px 28px; 
                          text-decoration: none; border-radius: 8px; font-weight: 600;
                          display: inline-block;">
                    {button_text}
                </a>
            </div>
            '''
        
        return f'''
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="utf-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
        </head>
        <body style="margin: 0; padding: 0; font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; background-color: #F8FAFC;">
            <div style="max-width: 600px; margin: 0 auto; padding: 40px 20px;">
                <!-- Header -->
                <div style="text-align: center; margin-bottom: 30px;">
                    <h1 style="color: #1E3A5F; font-size: 28px; margin: 0;">
                        🔬 LabBridge
                    </h1>
                </div>
                
                <!-- Card -->
                <div style="background: white; border-radius: 16px; padding: 40px; box-shadow: 0 4px 6px rgba(0,0,0,0.05);">
                    <h2 style="color: #1E3A5F; font-size: 22px; margin-top: 0;">
                        {title}
                    </h2>
                    
                    <div style="color: #64748B; font-size: 16px; line-height: 1.6;">
                        {content}
                    </div>
                    
                    {button_html}
                </div>
                
                <!-- Footer -->
                <div style="text-align: center; margin-top: 30px; color: #94A3B8; font-size: 14px;">
                    <p>© {datetime.now().year} LabBridge - Auditoria Inteligente para Laboratórios</p>
                    <p style="font-size: 12px;">
                        Este email foi enviado automaticamente. Por favor, não responda.
                    </p>
                </div>
            </div>
        </body>
        </html>
        '''
    
    def send_email(
        self, 
        to_email: str, 
        subject: str, 
        html_content: str,
        text_content: str = None
    ) -> Tuple[bool, str]:
        """
        Envia um email
        
        Returns:
            Tuple[success, message]
        """
        if not self.is_configured:
            # Modo simulado - apenas loga
            print(f"📧 [SIMULADO] Email para {to_email}")
            print(f"   Assunto: {subject}")
            return True, "Email enviado (modo simulado)"
        
        # Tenta Resend primeiro
        if self.resend_api_key:
            return self._send_via_resend(to_email, subject, html_content)
        
        # Fallback para SMTP
        return self._send_via_smtp(to_email, subject, html_content, text_content)
    
    def _send_via_smtp(
        self, 
        to_email: str, 
        subject: str, 
        html_content: str,
        text_content: str = None
    ) -> Tuple[bool, str]:
        """Envia email via SMTP"""
        try:
            message = MIMEMultipart("alternative")
            message["Subject"] = subject
            message["From"] = f"{self.from_name} <{self.from_email}>"
            message["To"] = to_email
            
            # Texto plano (fallback)
            if text_content:
                part1 = MIMEText(text_content, "plain")
                message.attach(part1)
            
            # HTML
            part2 = MIMEText(html_content, "html")
            message.attach(part2)
            
            # Conectar e enviar
            context = ssl.create_default_context()
            with smtplib.SMTP(self.smtp_host, self.smtp_port) as server:
                server.starttls(context=context)
                server.login(self.smtp_user, self.smtp_password)
                server.sendmail(self.from_email, to_email, message.as_string())
            
            return True, "Email enviado com sucesso"
        except Exception as e:
            print(f"Erro SMTP: {e}")
            return False, f"Erro ao enviar email: {str(e)}"
    
    def _send_via_resend(self, to_email: str, subject: str, html_content: str) -> Tuple[bool, str]:
        """Envia email via Resend API"""
        try:
            import resend
            resend.api_key = self.resend_api_key
            
            resend.Emails.send({
                "from": f"{self.from_name} <{self.from_email}>",
                "to": [to_email],
                "subject": subject,
                "html": html_content
            })
            return True, "Email enviado com sucesso"
        except ImportError:
            print("⚠️ Resend não instalado. Execute: pip install resend")
            return False, "Resend não instalado"
        except Exception as e:
            return False, f"Erro Resend: {str(e)}"
    
    # =========================================================================
    # TEMPLATES DE EMAIL
    # =========================================================================
    
    def send_team_invite(
        self, 
        to_email: str, 
        inviter_name: str, 
        role: str,
        invite_token: str,
        message: str = ""
    ) -> Tuple[bool, str]:
        """Envia convite para membro da equipe"""
        invite_url = f"{self.app_url}/invite/{invite_token}"
        
        role_names = {
            "admin": "Administrador",
            "analyst": "Analista",
            "viewer": "Visualizador"
        }
        role_display = role_names.get(role, role)
        
        content = f'''
        <p>Você foi convidado por <strong>{inviter_name}</strong> para fazer parte da equipe no LabBridge!</p>
        
        <p><strong>Cargo:</strong> {role_display}</p>
        
        {f'<p><strong>Mensagem:</strong> "{message}"</p>' if message else ''}
        
        <p>Clique no botão abaixo para aceitar o convite e criar sua conta:</p>
        '''
        
        html = self._get_html_template(
            title="Convite para o LabBridge",
            content=content,
            button_text="Aceitar Convite",
            button_url=invite_url
        )
        
        return self.send_email(
            to_email=to_email,
            subject=f"Convite para o LabBridge - {inviter_name}",
            html_content=html
        )
    
    def send_password_reset(self, to_email: str, reset_token: str) -> Tuple[bool, str]:
        """Envia email de recuperação de senha"""
        reset_url = f"{self.app_url}/reset-password/{reset_token}"
        
        content = '''
        <p>Recebemos uma solicitação para redefinir a senha da sua conta no LabBridge.</p>
        
        <p>Se você não fez esta solicitação, ignore este email.</p>
        
        <p>Este link expira em <strong>1 hora</strong>.</p>
        '''
        
        html = self._get_html_template(
            title="Redefinir Senha",
            content=content,
            button_text="Redefinir Senha",
            button_url=reset_url
        )
        
        return self.send_email(
            to_email=to_email,
            subject="Redefinir Senha - LabBridge",
            html_content=html
        )
    
    def send_welcome(self, to_email: str, user_name: str) -> Tuple[bool, str]:
        """Envia email de boas-vindas"""
        content = f'''
        <p>Olá <strong>{user_name}</strong>!</p>
        
        <p>Seja bem-vindo ao LabBridge - sua plataforma de auditoria inteligente para laboratórios.</p>
        
        <p>Com o LabBridge você pode:</p>
        <ul style="color: #64748B;">
            <li>Comparar arquivos COMPULAB × SIMUS automaticamente</li>
            <li>Identificar divergências financeiras em segundos</li>
            <li>Gerar relatórios profissionais em PDF</li>
            <li>Acompanhar histórico de auditorias</li>
        </ul>
        
        <p>Acesse agora e comece sua primeira análise!</p>
        '''
        
        html = self._get_html_template(
            title="Bem-vindo ao LabBridge! 🎉",
            content=content,
            button_text="Acessar LabBridge",
            button_url=self.app_url
        )
        
        return self.send_email(
            to_email=to_email,
            subject="Bem-vindo ao LabBridge! 🔬",
            html_content=html
        )
    
    def send_analysis_complete(
        self, 
        to_email: str, 
        analysis_name: str,
        compulab_total: float,
        simus_total: float,
        difference: float,
        divergences_count: int,
        report_url: str = None
    ) -> Tuple[bool, str]:
        """Envia notificação de análise concluída"""
        
        diff_color = "#DC2626" if difference > 0 else "#16A34A"
        
        content = f'''
        <p>Sua análise <strong>"{analysis_name}"</strong> foi concluída com sucesso!</p>
        
        <div style="background: #F8FAFC; border-radius: 8px; padding: 20px; margin: 20px 0;">
            <table style="width: 100%; border-collapse: collapse;">
                <tr>
                    <td style="padding: 8px 0; color: #64748B;">Faturamento COMPULAB:</td>
                    <td style="padding: 8px 0; text-align: right; font-weight: 600; color: #1E3A5F;">
                        R$ {compulab_total:,.2f}
                    </td>
                </tr>
                <tr>
                    <td style="padding: 8px 0; color: #64748B;">Faturamento SIMUS:</td>
                    <td style="padding: 8px 0; text-align: right; font-weight: 600; color: #1E3A5F;">
                        R$ {simus_total:,.2f}
                    </td>
                </tr>
                <tr style="border-top: 1px solid #E2E8F0;">
                    <td style="padding: 12px 0 8px; color: #64748B; font-weight: 600;">Diferença:</td>
                    <td style="padding: 12px 0 8px; text-align: right; font-weight: 700; color: {diff_color}; font-size: 18px;">
                        R$ {difference:,.2f}
                    </td>
                </tr>
                <tr>
                    <td style="padding: 8px 0; color: #64748B;">Divergências encontradas:</td>
                    <td style="padding: 8px 0; text-align: right; font-weight: 600; color: #F59E0B;">
                        {divergences_count}
                    </td>
                </tr>
            </table>
        </div>
        '''
        
        html = self._get_html_template(
            title="Análise Concluída ✅",
            content=content,
            button_text="Ver Relatório Completo",
            button_url=report_url or f"{self.app_url}/analise"
        )
        
        return self.send_email(
            to_email=to_email,
            subject=f"Análise Concluída: {analysis_name}",
            html_content=html
        )
    
    def send_critical_divergence_alert(
        self, 
        to_email: str, 
        analysis_name: str,
        divergence_value: float,
        patient_name: str = None,
        exam_name: str = None
    ) -> Tuple[bool, str]:
        """Envia alerta de divergência crítica"""
        
        content = f'''
        <p style="color: #DC2626; font-weight: 600;">⚠️ Divergência crítica detectada!</p>
        
        <p>Na análise <strong>"{analysis_name}"</strong>, foi identificada uma divergência significativa:</p>
        
        <div style="background: #FEF2F2; border: 1px solid #FECACA; border-radius: 8px; padding: 20px; margin: 20px 0;">
            <p style="margin: 0; color: #DC2626; font-size: 24px; font-weight: 700;">
                R$ {divergence_value:,.2f}
            </p>
            {f'<p style="margin: 10px 0 0; color: #991B1B;">Paciente: {patient_name}</p>' if patient_name else ''}
            {f'<p style="margin: 5px 0 0; color: #991B1B;">Exame: {exam_name}</p>' if exam_name else ''}
        </div>
        
        <p>Recomendamos verificar esta divergência o mais breve possível.</p>
        '''
        
        html = self._get_html_template(
            title="🚨 Alerta de Divergência",
            content=content,
            button_text="Verificar Agora",
            button_url=f"{self.app_url}/analise"
        )
        
        return self.send_email(
            to_email=to_email,
            subject=f"⚠️ Divergência Crítica: R$ {divergence_value:,.2f}",
            html_content=html
        )
    
    def send_subscription_confirmation(
        self, 
        to_email: str, 
        plan_name: str,
        amount: float,
        next_billing_date: str
    ) -> Tuple[bool, str]:
        """Envia confirmação de assinatura"""
        
        content = f'''
        <p>Sua assinatura do plano <strong>{plan_name}</strong> foi confirmada!</p>
        
        <div style="background: #F0FDF4; border: 1px solid #BBF7D0; border-radius: 8px; padding: 20px; margin: 20px 0;">
            <p style="margin: 0 0 10px; color: #166534;">✅ Pagamento confirmado</p>
            <p style="margin: 0; color: #15803D;">
                <strong>Valor:</strong> R$ {amount:,.2f}<br>
                <strong>Próxima cobrança:</strong> {next_billing_date}
            </p>
        </div>
        
        <p>Agora você tem acesso a todos os recursos do plano {plan_name}.</p>
        '''
        
        html = self._get_html_template(
            title="Assinatura Confirmada! 🎉",
            content=content,
            button_text="Acessar LabBridge",
            button_url=self.app_url
        )
        
        return self.send_email(
            to_email=to_email,
            subject=f"Assinatura Confirmada - Plano {plan_name}",
            html_content=html
        )


# Singleton
email_service = EmailService()

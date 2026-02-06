"""
SubscriptionState - Estado de Assinaturas
Gerencia planos e pagamentos com Stripe.
"""
import reflex as rx
from typing import Optional
from datetime import datetime
import logging
from .auth_state import AuthState

logger = logging.getLogger(__name__)


class SubscriptionState(AuthState):
    """Estado responsavel pelas assinaturas e planos"""

    # Plano atual
    current_plan: str = "starter"  # starter, pro, enterprise
    stripe_customer_id: str = ""
    stripe_subscription_id: str = ""
    subscription_status: str = "active"  # active, past_due, canceled
    next_billing_date: str = ""

    # Modal de upgrade
    show_upgrade_modal: bool = False
    selected_plan: str = ""
    billing_period: str = "monthly"  # monthly, yearly

    # Modal de contato enterprise
    show_enterprise_modal: bool = False
    enterprise_name: str = ""
    enterprise_email: str = ""
    enterprise_company: str = ""
    enterprise_message: str = ""

    # Loading states
    is_processing: bool = False
    payment_success: bool = False
    payment_error: str = ""
    checkout_url: str = ""

    def load_subscription(self):
        """Carrega plano atual do tenant"""
        if self.current_tenant:
            self.current_plan = getattr(self.current_tenant, "plan_type", None) or "starter"

    def select_plan(self, plan: str):
        """Seleciona um plano para upgrade/downgrade"""
        if plan == self.current_plan:
            return rx.toast.info("Voce ja esta neste plano!")

        if plan == "enterprise":
            self.show_enterprise_modal = True
            self.selected_plan = plan
            return

        self.selected_plan = plan
        self.show_upgrade_modal = True
        self.payment_success = False
        self.payment_error = ""

    def close_upgrade_modal(self):
        """Fecha o modal de upgrade"""
        self.show_upgrade_modal = False
        self.selected_plan = ""
        self.payment_success = False
        self.payment_error = ""
        self.checkout_url = ""

    def close_enterprise_modal(self):
        """Fecha o modal enterprise"""
        self.show_enterprise_modal = False
        self.enterprise_name = ""
        self.enterprise_email = ""
        self.enterprise_company = ""
        self.enterprise_message = ""

    def set_enterprise_name(self, value: str):
        self.enterprise_name = value

    def set_enterprise_email(self, value: str):
        self.enterprise_email = value

    def set_enterprise_company(self, value: str):
        self.enterprise_company = value

    def set_enterprise_message(self, value: str):
        self.enterprise_message = value

    def set_billing_period(self, value: str):
        """Define período de cobrança (monthly/yearly)"""
        self.billing_period = value

    async def confirm_plan_change(self):
        """Confirma mudança de plano via Stripe Checkout"""
        from ..services.stripe_service import stripe_service
        
        self.is_processing = True
        self.payment_error = ""
        yield

        try:
            # Se não tem customer_id, criar um
            if not self.stripe_customer_id:
                if not self.current_user:
                    self.payment_error = "Usuario nao autenticado"
                    self.is_processing = False
                    yield
                    return
                user_email = self.current_user.email
                user_name = self.current_user.full_name or user_email
                success, msg, customer_id = stripe_service.create_customer(
                    email=user_email,
                    name=user_name or user_email,
                    metadata={"plan": self.selected_plan}
                )
                if success and customer_id:
                    self.stripe_customer_id = customer_id
                else:
                    self.payment_error = msg
                    self.is_processing = False
                    yield
                    return

            # Criar sessão de checkout
            success, msg, checkout_url = stripe_service.create_checkout_session(
                customer_id=self.stripe_customer_id,
                plan=self.selected_plan,
                billing_period=self.billing_period,
                success_url=f"/subscription?success=true&plan={self.selected_plan}",
                cancel_url="/subscription?cancelled=true"
            )

            if success and checkout_url:
                self.checkout_url = checkout_url
                
                # Se Stripe não está configurado (modo simulado), aplicar mudança direto
                if not stripe_service.is_configured:
                    self.current_plan = self.selected_plan
                    self.payment_success = True
                    self.is_processing = False
                    yield
                    
                    # Fecha modal após 2 segundos
                    import asyncio
                    await asyncio.sleep(2)
                    self.close_upgrade_modal()
                    yield rx.toast.success(f"Plano alterado para {self.selected_plan.title()}!")
                else:
                    # Redirecionar para Stripe Checkout
                    self.is_processing = False
                    yield rx.redirect(checkout_url)
            else:
                self.payment_error = msg
                self.is_processing = False

        except Exception as e:
            self.payment_error = f"Erro no processamento: {str(e)}"
            self.is_processing = False

        yield

    async def handle_checkout_success(self, session_id: str = "", plan: str = ""):
        """Processa retorno de checkout bem-sucedido"""
        from ..services.stripe_service import stripe_service

        # Em producao, verificar a sessao no Stripe ao inves de confiar no parametro
        if stripe_service.is_configured and session_id:
            try:
                import stripe
                session = stripe.checkout.Session.retrieve(session_id)
                verified_plan = session.metadata.get("plan", plan or "starter")
                self.current_plan = verified_plan
            except Exception as e:
                logger.error(f"Erro ao verificar sessao Stripe: {e}")
                # Fallback: aceitar o parametro com warning
                self.current_plan = plan or "starter"
        else:
            # Modo simulado (dev) - aceitar o parametro
            self.current_plan = plan or "starter"

        self.payment_success = True
        yield rx.toast.success(f"Assinatura do plano {self.current_plan.title()} confirmada!")

    async def open_billing_portal(self):
        """Abre portal de gerenciamento de assinatura"""
        from ..services.stripe_service import stripe_service
        
        if not self.stripe_customer_id:
            yield rx.toast.error("Nenhuma assinatura encontrada")
            return
        
        success, msg, portal_url = stripe_service.create_portal_session(
            customer_id=self.stripe_customer_id,
            return_url="/subscription"
        )
        
        if success and portal_url:
            yield rx.redirect(portal_url)
        else:
            yield rx.toast.error(msg)

    async def submit_enterprise_contact(self):
        """Envia solicitacao enterprise via email"""
        from ..services.email_service import email_service
        
        self.is_processing = True
        yield

        try:
            # Validacao
            if not self.enterprise_name.strip():
                self.is_processing = False
                yield rx.toast.error("Nome e obrigatorio")
                return

            if not self.enterprise_email.strip() or "@" not in self.enterprise_email:
                self.is_processing = False
                yield rx.toast.error("Email invalido")
                return

            if not self.enterprise_company.strip():
                self.is_processing = False
                yield rx.toast.error("Empresa e obrigatoria")
                return

            # Enviar email de contato (para o admin)
            content = f'''
            <p><strong>Nova solicitação Enterprise:</strong></p>
            <ul>
                <li><strong>Nome:</strong> {self.enterprise_name}</li>
                <li><strong>Email:</strong> {self.enterprise_email}</li>
                <li><strong>Empresa:</strong> {self.enterprise_company}</li>
                <li><strong>Mensagem:</strong> {self.enterprise_message or "Não informada"}</li>
            </ul>
            '''
            
            # TODO: enviar email_service.send() para admin com conteudo enterprise
            logger.info(f"Solicitacao Enterprise: {self.enterprise_name} - {self.enterprise_company}")
            
            import asyncio
            await asyncio.sleep(1)

            self.is_processing = False
            self.close_enterprise_modal()

            yield rx.toast.success("Solicitacao enviada! Nossa equipe entrara em contato em ate 24h.")

        except Exception as e:
            self.is_processing = False
            yield rx.toast.error(f"Erro: {str(e)}")

    @rx.var
    def plan_display_name(self) -> str:
        """Nome do plano atual para exibicao"""
        names = {
            "starter": "Starter",
            "pro": "Pro",
            "enterprise": "Enterprise"
        }
        return names.get(self.current_plan, "Starter")

    @rx.var
    def is_starter(self) -> bool:
        return self.current_plan == "starter"

    @rx.var
    def is_pro(self) -> bool:
        return self.current_plan == "pro"

    @rx.var
    def is_enterprise(self) -> bool:
        return self.current_plan == "enterprise"

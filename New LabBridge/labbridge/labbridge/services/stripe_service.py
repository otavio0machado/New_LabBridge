"""
Stripe Service - Integração com Stripe para pagamentos
LabBridge
"""
import logging
import os
from typing import Dict, Any, Optional, Tuple
from datetime import datetime

logger = logging.getLogger(__name__)


class StripeService:
    """Serviço de integração com Stripe"""
    
    def __init__(self):
        self.api_key = os.getenv("STRIPE_SECRET_KEY", "")
        self.public_key = os.getenv("STRIPE_PUBLIC_KEY", "")
        self.webhook_secret = os.getenv("STRIPE_WEBHOOK_SECRET", "")
        self._stripe = None
        
        # Preços dos planos (IDs do Stripe)
        self.price_ids = {
            "starter_monthly": os.getenv("STRIPE_PRICE_STARTER_MONTHLY", "price_starter_monthly"),
            "starter_yearly": os.getenv("STRIPE_PRICE_STARTER_YEARLY", "price_starter_yearly"),
            "pro_monthly": os.getenv("STRIPE_PRICE_PRO_MONTHLY", "price_pro_monthly"),
            "pro_yearly": os.getenv("STRIPE_PRICE_PRO_YEARLY", "price_pro_yearly"),
            "enterprise_monthly": os.getenv("STRIPE_PRICE_ENTERPRISE_MONTHLY", "price_enterprise_monthly"),
            "enterprise_yearly": os.getenv("STRIPE_PRICE_ENTERPRISE_YEARLY", "price_enterprise_yearly"),
        }
        
        # Valores em centavos (para modo de teste sem Stripe)
        self.plan_prices = {
            "starter": {"monthly": 9900, "yearly": 99000},  # R$ 99/mês ou R$ 990/ano
            "pro": {"monthly": 19900, "yearly": 199000},     # R$ 199/mês ou R$ 1990/ano
            "enterprise": {"monthly": 49900, "yearly": 499000},  # R$ 499/mês ou R$ 4990/ano
        }
    
    @property
    def stripe(self):
        """Lazy loading do módulo stripe"""
        if self._stripe is None:
            try:
                import stripe
                stripe.api_key = self.api_key
                self._stripe = stripe
            except ImportError:
                logger.warning("Stripe nao instalado. Execute: pip install stripe")
                return None
        return self._stripe
    
    @property
    def is_configured(self) -> bool:
        """Verifica se o Stripe está configurado"""
        return bool(self.api_key and self.public_key)
    
    def create_customer(self, email: str, name: str, metadata: Dict[str, Any] = None) -> Tuple[bool, str, Optional[str]]:
        """
        Cria um cliente no Stripe
        
        Returns:
            Tuple[success, message, customer_id]
        """
        if not self.is_configured:
            # Modo simulado
            return True, "Cliente criado (modo simulado)", f"cus_simulated_{datetime.now().timestamp()}"
        
        try:
            customer = self.stripe.Customer.create(
                email=email,
                name=name,
                metadata=metadata or {}
            )
            return True, "Cliente criado com sucesso", customer.id
        except Exception as e:
            return False, f"Erro ao criar cliente: {str(e)}", None
    
    def create_checkout_session(
        self, 
        customer_id: str, 
        plan: str, 
        billing_period: str = "monthly",
        success_url: str = "/subscription?success=true",
        cancel_url: str = "/subscription?cancelled=true"
    ) -> Tuple[bool, str, Optional[str]]:
        """
        Cria uma sessão de checkout do Stripe
        
        Returns:
            Tuple[success, message, checkout_url]
        """
        if not self.is_configured:
            # Modo simulado - retorna URL de sucesso direto
            return True, "Checkout simulado", success_url
        
        try:
            price_key = f"{plan}_{billing_period}"
            price_id = self.price_ids.get(price_key)
            
            if not price_id:
                return False, f"Plano não encontrado: {price_key}", None
            
            session = self.stripe.checkout.Session.create(
                customer=customer_id,
                payment_method_types=["card"],
                line_items=[{
                    "price": price_id,
                    "quantity": 1,
                }],
                mode="subscription",
                success_url=success_url,
                cancel_url=cancel_url,
                metadata={
                    "plan": plan,
                    "billing_period": billing_period
                }
            )
            return True, "Checkout criado", session.url
        except Exception as e:
            return False, f"Erro ao criar checkout: {str(e)}", None
    
    def create_portal_session(self, customer_id: str, return_url: str = "/subscription") -> Tuple[bool, str, Optional[str]]:
        """
        Cria uma sessão do portal do cliente para gerenciar assinatura
        
        Returns:
            Tuple[success, message, portal_url]
        """
        if not self.is_configured:
            return True, "Portal simulado", return_url
        
        try:
            session = self.stripe.billing_portal.Session.create(
                customer=customer_id,
                return_url=return_url
            )
            return True, "Portal criado", session.url
        except Exception as e:
            return False, f"Erro ao criar portal: {str(e)}", None
    
    def get_subscription(self, subscription_id: str) -> Tuple[bool, str, Optional[Dict[str, Any]]]:
        """
        Busca detalhes de uma assinatura
        
        Returns:
            Tuple[success, message, subscription_data]
        """
        if not self.is_configured:
            return True, "Assinatura simulada", {
                "id": subscription_id,
                "status": "active",
                "plan": "pro",
                "current_period_end": datetime.now().timestamp() + (30 * 24 * 60 * 60)
            }
        
        try:
            subscription = self.stripe.Subscription.retrieve(subscription_id)
            return True, "Sucesso", {
                "id": subscription.id,
                "status": subscription.status,
                "current_period_end": subscription.current_period_end,
                "cancel_at_period_end": subscription.cancel_at_period_end
            }
        except Exception as e:
            return False, f"Erro ao buscar assinatura: {str(e)}", None
    
    def cancel_subscription(self, subscription_id: str, at_period_end: bool = True) -> Tuple[bool, str]:
        """
        Cancela uma assinatura
        
        Args:
            subscription_id: ID da assinatura
            at_period_end: Se True, cancela no fim do período atual
        
        Returns:
            Tuple[success, message]
        """
        if not self.is_configured:
            return True, "Assinatura cancelada (simulado)"
        
        try:
            if at_period_end:
                self.stripe.Subscription.modify(
                    subscription_id,
                    cancel_at_period_end=True
                )
                return True, "Assinatura será cancelada no fim do período atual"
            else:
                self.stripe.Subscription.delete(subscription_id)
                return True, "Assinatura cancelada imediatamente"
        except Exception as e:
            return False, f"Erro ao cancelar: {str(e)}"
    
    def verify_webhook(self, payload: bytes, signature: str) -> Tuple[bool, str, Optional[Dict[str, Any]]]:
        """
        Verifica e processa webhook do Stripe
        
        Returns:
            Tuple[success, message, event_data]
        """
        if not self.is_configured or not self.webhook_secret:
            return False, "Webhook não configurado", None
        
        try:
            event = self.stripe.Webhook.construct_event(
                payload, signature, self.webhook_secret
            )
            return True, "Webhook válido", {
                "type": event.type,
                "data": event.data.object
            }
        except Exception as e:
            return False, f"Webhook inválido: {str(e)}", None
    
    def process_successful_payment(self, event_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Processa evento de pagamento bem-sucedido
        
        Returns:
            Dict com informações do pagamento processado
        """
        return {
            "status": "processed",
            "subscription_id": event_data.get("subscription"),
            "customer_id": event_data.get("customer"),
            "amount": event_data.get("amount_total", 0) / 100,
            "currency": event_data.get("currency", "brl")
        }


# Singleton
stripe_service = StripeService()

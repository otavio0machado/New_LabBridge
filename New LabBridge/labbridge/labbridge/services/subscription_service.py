from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
from ..models import Subscription, Plan, Tenant

class SubscriptionService:
    """
    Serviço para gerenciar assinaturas, planos e limites.
    """
    
    def __init__(self):
        # MOCK: In memory storage for dev
        self._plans = {
            "starter": Plan(id="starter", name="Starter", price=0.00, features=["Basic"], limits={"analyses": 50}),
            "pro": Plan(id="pro", name="Pro", price=299.00, features=["Advanced", "AI"], limits={"analyses": -1}),
            "enterprise": Plan(id="enterprise", name="Enterprise", price=0.00, features=["All"], limits={"analyses": -1})
        }
        
    def get_plans(self) -> List[Plan]:
        """Retorna todos os planos disponíveis."""
        return list(self._plans.values())
        
    def get_tenant_subscription(self, tenant_id: str) -> Optional[Subscription]:
        """
        Retorna a assinatura ativa de um tenant.
        TODO: buscar no Supabase (tabela subscriptions) em vez de mock.
        """
        return Subscription(
            id=f"sub_{tenant_id}",
            tenant_id=tenant_id,
            plan_id="pro", # Mock: todos são Pro por enquanto
            status="active",
            current_period_start=datetime.now().isoformat(),
            current_period_end=(datetime.now() + timedelta(days=30)).isoformat(),
            created_at=datetime.now().isoformat()
        )
        
    def upgrade_plan(self, tenant_id: str, new_plan_id: str) -> Dict[str, Any]:
        """
        Atualiza o plano de um tenant.
        """
        if new_plan_id not in self._plans:
            return {"success": False, "message": "Plano inválido"}
            
        # MOCK: Lógica de atualização
        # Aqui integraria com Stripe para criar Checkout Session
        
        return {
            "success": True, 
            "message": f"Plano atualizado para {self._plans[new_plan_id].name}",
            "plan_id": new_plan_id
        }
        
    def check_limit(self, tenant_id: str, feature: str) -> bool:
        """
        Verifica se o tenant pode usar uma feature ou atingiu limite.
        """
        sub = self.get_tenant_subscription(tenant_id)
        if not sub or sub.status != "active":
            return False
            
        plan = self._plans.get(sub.plan_id)
        if not plan:
            return False
            
        # Lógica de verificação de limites (ex: count de análises no mês)
        return True # Mock: sempre permitido

subscription_service = SubscriptionService()

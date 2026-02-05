import reflex as rx
from typing import List, Optional, Any, Dict
from pydantic import BaseModel


class Plan(BaseModel):
    """Modelo de Plano de Assinatura"""
    id: str
    name: str # Starter, Pro, Enterprise
    price: float
    currency: str = "BRL"
    features: List[str] = []
    limits: Dict[str, Any] = {} # {"analyses_per_month": 50, "users": 1}

class Subscription(BaseModel):
    """Modelo de Assinatura"""
    id: str
    tenant_id: str
    plan_id: str
    status: str # active, past_due, canceled, trialing
    current_period_start: str
    current_period_end: str
    stripe_subscription_id: Optional[str] = None
    created_at: str

class Tenant(BaseModel):
    """Modelo de Cliente (Laboratório)"""
    id: str
    name: str = ""
    # Dados de Contato/Fiscal
    cnpj: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None
    
    # Plano Atual
    plan_type: str = "starter" # starter, pro, enterprise
    subscription_status: str = "active"
    
    # Billing
    stripe_customer_id: Optional[str] = None
    
    # Configurações
    settings: Dict[str, Any] = {
        "analysis_threshold": 0.05,
        "auto_detect_typos": True,
        "theme": "light"
    }
    created_at: str = ""

class User(BaseModel):
    """Modelo de Usuário SaaS"""
    id: str
    email: str
    tenant_id: str
    role: str = "member" # owner, admin, member
    created_at: str = ""

class AnalysisResult(BaseModel):
    """Resultado de uma análise individual"""
    patient: str = ""
    exam_name: str = ""
    value: float = 0.0
    compulab_value: float = 0.0
    simus_value: float = 0.0
    difference: float = 0.0
    compulab_count: int = 0
    simus_count: int = 0
    exams_count: int = 0
    total_value: float = 0.0
    tenant_id: str = ""





class PatientHistoryEntry(BaseModel):
    """Entrada de histórico do paciente"""
    id: str = ""
    patient_name: str = ""
    exam_name: str = ""
    status: str = ""
    last_value: float = 0.0
    notes: str = ""
    created_at: str = ""
    tenant_id: str = ""


class PatientModel(BaseModel):
    """Modelo simplificado de paciente"""
    name: str = ""
    total_exams: int = 0
    total_value: float = 0.0
    tenant_id: str = ""


class TopOffender(BaseModel):
    """Modelo de ofensor (exame/problema recorrente)"""
    name: str = ""
    count: int = 0


# =============================================================================
# TEAM MANAGEMENT MODELS
# =============================================================================

class TeamMember(BaseModel):
    """Modelo de membro da equipe"""
    id: str = ""
    email: str = ""
    name: str = ""
    role: str = "viewer"  # admin_global, admin_lab, analyst, viewer
    status: str = "pending"  # active, pending, inactive
    tenant_id: str = ""
    invited_by: str = ""
    last_active: Optional[str] = None
    created_at: str = ""

    @property
    def role_display(self) -> str:
        """Nome do papel para exibição"""
        roles = {
            "admin_global": "Admin Global",
            "admin_lab": "Admin Lab",
            "analyst": "Analista",
            "viewer": "Visualizador"
        }
        return roles.get(self.role, "Visualizador")


class TeamInvite(BaseModel):
    """Modelo de convite para equipe"""
    id: str = ""
    email: str = ""
    role: str = "viewer"
    tenant_id: str = ""
    invited_by: str = ""
    token: str = ""
    message: str = ""
    status: str = "pending"  # pending, accepted, expired
    expires_at: str = ""
    created_at: str = ""


# =============================================================================
# INTEGRATION MODELS
# =============================================================================

class Integration(BaseModel):
    """Modelo de integração externa"""
    id: str = ""
    name: str = ""
    description: str = ""
    category: str = ""  # lis, billing, storage, communication
    icon: str = ""
    status: str = "inactive"  # active, inactive, error, syncing
    tenant_id: str = ""
    config: Dict[str, Any] = {}  # Configurações específicas da integração
    credentials: Dict[str, Any] = {}  # Credenciais (criptografadas)
    last_sync: Optional[str] = None
    last_error: Optional[str] = None
    created_at: str = ""
    updated_at: str = ""


class IntegrationLog(BaseModel):
    """Log de atividade da integração"""
    id: str = ""
    integration_id: str = ""
    action: str = ""  # sync, connect, disconnect, error
    status: str = ""  # success, error
    message: str = ""
    details: Dict[str, Any] = {}
    created_at: str = ""

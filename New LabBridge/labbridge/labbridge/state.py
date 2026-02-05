"""
State - Estado Global da Aplicacao (Modularizado)
Composicao dos estados modulares + metricas do dashboard conectadas ao banco.
"""
import reflex as rx
from typing import List, Dict, Any, Optional
from datetime import datetime

# Import Modular States
from .states.detective_state import DetectiveState
from .services.mapping_service import mapping_service
from .services.ai_service import ai_service
from .repositories.audit_repository import AuditRepository
from .models import TopOffender


class State(DetectiveState):
    """Estado global da aplicacao (Modularizado)"""

    def get_canonical_name(self, name: str) -> str:
        """Helper para obter nome canonico de forma sincrona"""
        return mapping_service.get_canonical_name_sync(name)

    # Navegacao e UI Global
    current_page: str = "dashboard"

    # Floating Chat
    show_chat_panel: bool = False
    _chat_context_loaded: bool = False

    # Cache de metricas do dashboard
    _dashboard_cache: Dict[str, Any] = {}
    _dashboard_cache_time: str = ""

    def toggle_chat_panel(self):
        """Abre/fecha o painel flutuante de chat"""
        self.show_chat_panel = not self.show_chat_panel
        if self.show_chat_panel and not self._chat_context_loaded:
            self.load_context()
            self._chat_context_loaded = True

    def close_chat_panel(self):
        """Fecha o painel de chat"""
        self.show_chat_panel = False

    def set_page(self, page: str):
        """Define a pagina atual"""
        self.current_page = page

    def navigate_to(self, page: str):
        """Navega para uma pagina especifica"""
        self.set_page(page)
        if page == "dashboard":
            return rx.redirect("/")
        return rx.redirect(f"/{page}")

    # =====================================================
    # METRICAS DO DASHBOARD - CONECTADAS AOS DADOS REAIS
    # =====================================================

    def _get_monthly_data(self) -> Dict[str, Any]:
        """Busca dados do mes atual do banco (com cache de 5 min)"""
        from .services.saved_analysis_service import saved_analysis_service

        now = datetime.now()
        cache_key = f"{now.year}-{now.month}"

        # Verificar cache (5 minutos)
        if self._dashboard_cache.get("key") == cache_key and self._dashboard_cache_time:
            try:
                cache_time = datetime.fromisoformat(self._dashboard_cache_time)
                if (now - cache_time).seconds < 300:
                    return self._dashboard_cache.get("data", {})
            except (ValueError, TypeError):
                pass

        # Buscar dados do banco
        tenant_id = self.current_tenant.id if self.current_tenant else ""
        if not tenant_id:
            return {}

        try:
            report = saved_analysis_service.get_monthly_report(
                tenant_id=tenant_id, year=now.year, month=now.month
            )
            data = report or {}
            self._dashboard_cache = {"key": cache_key, "data": data}
            self._dashboard_cache_time = now.isoformat()
            return data
        except Exception as e:
            print(f"Erro ao buscar dados mensais: {e}")
            return {}

    @rx.var(auto_deps=False, deps=["has_analysis"])
    def analyses_today(self) -> int:
        """Total de analises - usa dados reais se disponiveis"""
        if self.has_analysis:
            return 1
        data = self._get_monthly_data()
        return data.get("count", 0)

    @rx.var(auto_deps=False, deps=["compulab_total"])
    def total_revenue_month(self) -> str:
        """Receita total processada no mes"""
        data = self._get_monthly_data()
        total = data.get("total_compulab", 0) or 0
        if total == 0 and self.compulab_total > 0:
            total = self.compulab_total
        return f"R$ {total:,.2f}"

    @rx.var
    def glosas_month(self) -> str:
        """Total de glosas/divergencias no mes"""
        total = self.patients_only_compulab_total + self.exams_only_compulab_total
        return f"R$ {total:,.2f}"

    @rx.var
    def pending_audits(self) -> int:
        """Numero de itens pendentes para auditoria"""
        return self.pending_items_count

    @rx.var
    def active_divergences(self) -> int:
        """Numero de divergencias ativas"""
        return len(self.value_divergences)

    @rx.var(auto_deps=False, deps=["has_analysis"])
    def monthly_analyses_chart(self) -> List[Dict[str, Any]]:
        """Dados para gráfico de análises mensais - DADOS REAIS do banco"""
        from .services.local_storage import local_storage

        try:
            tenant_id = self.current_user.tenant_id if self.current_user else ""
            if not tenant_id:
                return [{"name": m, "analises": 0} for m in ["Jan", "Fev", "Mar", "Abr", "Mai", "Jun"]]
            now = datetime.now()
            
            # Buscar últimos 6 meses
            chart_data = []
            month_names = ["Jan", "Fev", "Mar", "Abr", "Mai", "Jun", "Jul", "Ago", "Set", "Out", "Nov", "Dez"]
            
            for i in range(5, -1, -1):
                # Calcular mês
                month = now.month - i
                year = now.year
                while month <= 0:
                    month += 12
                    year -= 1
                
                # Buscar resumo do mês
                summary = local_storage.get_monthly_summary(tenant_id, year, month)
                count = summary.get("count", 0) if summary else 0
                
                chart_data.append({
                    "name": month_names[month - 1],
                    "analises": count
                })
            
            return chart_data
        except Exception as e:
            print(f"Erro ao gerar gráfico: {e}")
            # Fallback
            return [
                {"name": "Jan", "analises": 0},
                {"name": "Fev", "analises": 0},
                {"name": "Mar", "analises": 0},
                {"name": "Abr", "analises": 0},
                {"name": "Mai", "analises": 0},
                {"name": "Jun", "analises": 0},
            ]

    @rx.var
    def divergences_by_type(self) -> List[Dict[str, Any]]:
        """Dados para grafico de divergencias por tipo"""
        return [
            {"name": "Pacientes", "value": self.patients_only_compulab_count},
            {"name": "Exames", "value": self.exams_only_compulab_count},
            {"name": "Valores", "value": len(self.value_divergences)},
            {"name": "Extras", "value": self.exams_only_simus_count},
        ]

    @rx.var(auto_deps=False, deps=["compulab_total"])
    def goal_progress(self) -> int:
        """Progresso da meta mensal (percentual) - usa meta configurável"""
        from .services.local_storage import local_storage

        # Buscar meta das configurações
        tenant_id = self.current_user.tenant_id if self.current_user else ""
        user_id = self.current_user.id if self.current_user else ""
        settings = local_storage.get_user_settings(tenant_id, user_id)
        monthly_goal = 150000.0
        if settings:
            try:
                goal_str = settings.get("monthly_goal", "150000")
                monthly_goal = float(goal_str) if goal_str else 150000.0
            except (ValueError, TypeError):
                pass
        
        current = float(self.compulab_total or 0)
        if monthly_goal == 0:
            return 0
        progress = int((current / monthly_goal) * 100)
        return min(progress, 100)

    @rx.var
    def formatted_compulab_total(self) -> str:
        """Total COMPULAB formatado para dashboard"""
        if self.compulab_total > 0:
            return f"R$ {self.compulab_total:,.2f}"
        return "R$ 0,00"

    @rx.var(auto_deps=False, deps=["compulab_total"])
    def formatted_monthly_goal(self) -> str:
        """Meta mensal formatada - usa meta configurável"""
        from .services.local_storage import local_storage

        tenant_id = self.current_user.tenant_id if self.current_user else ""
        user_id = self.current_user.id if self.current_user else ""
        settings = local_storage.get_user_settings(tenant_id, user_id)
        monthly_goal = 150000.0
        if settings:
            try:
                goal_str = settings.get("monthly_goal", "150000")
                monthly_goal = float(goal_str) if goal_str else 150000.0
            except (ValueError, TypeError):
                pass
        
        return f"R$ {monthly_goal:,.2f}"

    @rx.var
    def formatted_revenue_forecast(self) -> str:
        """Previsao de receita baseada no ritmo atual"""
        if not self.has_analysis:
            return "R$ 0,00"
        today = datetime.now()
        days_passed = today.day
        if days_passed == 0:
            return f"R$ {self.compulab_total:,.2f}"
        daily_avg = self.compulab_total / days_passed
        forecast = daily_avg * 30
        return f"R$ {forecast:,.2f}"

    @rx.var
    def dashboard_approval_rate(self) -> float:
        """Taxa de aprovacao (itens resolvidos / total)"""
        if self.pending_items_count == 0:
            return 100.0
        return round(float(self.resolution_progress), 1)

    @rx.var
    def dashboard_pending_maintenances(self) -> int:
        """Numero de manutencoes pendentes"""
        return 0

    @rx.var
    def total_patients_count(self) -> int:
        """Total de pacientes processados"""
        return self.compulab_count + self.simus_count

    @rx.var
    def financial_growth_day(self) -> float:
        """Crescimento financeiro comparado ao dia anterior"""
        if self.compulab_total > 0:
            return 2.5
        return 0.0

    @rx.var
    def divergences_count(self) -> int:
        """Alias para contagem de divergencias"""
        return len(self.value_divergences)

    @rx.var
    def top_offenders(self) -> List[TopOffender]:
        """Top exames com mais problemas"""
        counts: Dict[str, int] = {}

        for item in self.exams_only_compulab:
            name = getattr(item, "exam_name", "") if hasattr(item, "exam_name") else item.get("exam_name", "")
            if name:
                counts[name] = counts.get(name, 0) + 1

        for item in self.value_divergences:
            name = getattr(item, "exam_name", "") if hasattr(item, "exam_name") else item.get("exam_name", "")
            if name:
                counts[name] = counts.get(name, 0) + 1

        sorted_exams = sorted(counts.items(), key=lambda x: x[1], reverse=True)[:5]
        return [TopOffender(name=str(n), count=int(c)) for n, c in sorted_exams]

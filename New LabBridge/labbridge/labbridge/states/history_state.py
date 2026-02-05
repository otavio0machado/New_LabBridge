"""
HistoryState - Estado do Histórico de Auditorias
Gerencia filtros, exportação e logs de atividades REAIS.
"""
import reflex as rx
from typing import List, Dict, Any
from datetime import datetime, timedelta
import base64


class HistoryState(rx.State):
    """Estado responsável pelo histórico de auditorias"""

    # Filtros
    status_filter: str = "Todas"
    date_filter: str = "Ultimo Mes"
    search_query: str = ""

    # Exportação
    is_exporting: bool = False

    # Log de atividades (do banco)
    activity_log: List[Dict[str, Any]] = []
    
    # Análises filtradas
    filtered_analyses: List[Dict[str, Any]] = []
    
    # Estatísticas do período
    period_stats: Dict[str, Any] = {}

    # =========================================================================
    # SETTERS
    # =========================================================================

    def set_status_filter(self, value: str):
        """Filtra por status"""
        self.status_filter = value

    def set_date_filter(self, value: str):
        """Filtra por data"""
        self.date_filter = value

    def set_search_query(self, value: str):
        """Filtra por busca"""
        self.search_query = value

    # =========================================================================
    # COMPUTED VARS
    # =========================================================================

    @rx.var
    def filtered_status(self) -> str:
        """Retorna o status para filtro"""
        status_map = {
            "Todas": "",
            "Concluidas": "completed",
            "Em Analise": "processing",
            "Pendentes": "pending",
        }
        return status_map.get(self.status_filter, "")

    @rx.var
    def stats_total_analyses(self) -> int:
        """Total de análises no período"""
        return self.period_stats.get("total", 0)

    @rx.var
    def stats_total_compulab(self) -> str:
        """Total COMPULAB no período"""
        total = self.period_stats.get("total_compulab", 0)
        return f"R$ {total:,.2f}"

    @rx.var
    def stats_total_simus(self) -> str:
        """Total SIMUS no período"""
        total = self.period_stats.get("total_simus", 0)
        return f"R$ {total:,.2f}"

    @rx.var
    def stats_total_difference(self) -> str:
        """Diferença total no período"""
        diff = self.period_stats.get("total_difference", 0)
        return f"R$ {diff:,.2f}"

    # =========================================================================
    # DATA LOADING
    # =========================================================================

    def _get_date_range(self) -> tuple:
        """Retorna range de datas baseado no filtro"""
        now = datetime.now()
        
        if self.date_filter == "Hoje":
            start = now.replace(hour=0, minute=0, second=0)
        elif self.date_filter == "Ultima Semana":
            start = now - timedelta(days=7)
        elif self.date_filter == "Ultimo Mes":
            start = now - timedelta(days=30)
        elif self.date_filter == "Ultimos 3 Meses":
            start = now - timedelta(days=90)
        elif self.date_filter == "Ultimo Ano":
            start = now - timedelta(days=365)
        else:
            start = now - timedelta(days=30)
        
        return (start.strftime("%Y-%m-%d"), now.strftime("%Y-%m-%d"))

    async def load_history_data(self):
        """Carrega histórico filtrado do banco"""
        from ..services.local_storage import local_storage
        
        try:
            tenant_id = "local"
            
            # Buscar análises
            all_analyses = local_storage.get_saved_analyses(tenant_id, limit=500)
            
            # Aplicar filtros
            filtered = []
            start_date, end_date = self._get_date_range()
            
            for analysis in all_analyses:
                # Filtro de data
                analysis_date = analysis.get("analysis_date", "")
                if analysis_date:
                    if analysis_date < start_date or analysis_date > end_date:
                        continue
                
                # Filtro de status
                if self.filtered_status:
                    analysis_status = analysis.get("status", "completed")
                    if analysis_status != self.filtered_status:
                        continue
                
                # Filtro de busca
                if self.search_query:
                    query = self.search_query.lower()
                    name = analysis.get("analysis_name", "").lower()
                    if query not in name:
                        continue
                
                filtered.append(analysis)
            
            self.filtered_analyses = filtered
            
            # Calcular estatísticas do período
            total_compulab = sum(a.get("compulab_total", 0) or 0 for a in filtered)
            total_simus = sum(a.get("simus_total", 0) or 0 for a in filtered)
            
            self.period_stats = {
                "total": len(filtered),
                "total_compulab": total_compulab,
                "total_simus": total_simus,
                "total_difference": total_compulab - total_simus,
            }
            
            # Carregar logs de atividade
            self._load_activity_log()
            
        except Exception as e:
            print(f"Erro ao carregar histórico: {e}")

    def load_activity_log(self):
        """Carrega log de atividades do banco"""
        from ..services.local_storage import local_storage
        
        try:
            tenant_id = "local"
            logs = local_storage.get_activity_logs(tenant_id, limit=50)
            self.activity_log = logs
        except Exception as e:
            print(f"Erro ao carregar logs: {e}")
            self.activity_log = []

    # =========================================================================
    # ACTIVITY LOGGING
    # =========================================================================

    def log_activity(self, action: str, details: str = "", user: str = "Sistema"):
        """Registra uma atividade no log"""
        from ..services.local_storage import local_storage
        
        try:
            local_storage.add_activity_log(
                tenant_id="local",
                action=action,
                details=details,
                user=user
            )
        except Exception as e:
            print(f"Erro ao registrar atividade: {e}")

    # =========================================================================
    # EXPORT
    # =========================================================================

    async def export_logs(self):
        """Exporta logs de atividades como CSV"""
        self.is_exporting = True
        yield

        try:
            # Gerar CSV real
            csv_lines = ["Data,Hora,Acao,Usuario,Detalhes"]
            
            for log in self.activity_log:
                timestamp = log.get("created_at", "")
                if "T" in str(timestamp):
                    date_part, time_part = str(timestamp).split("T")
                    time_part = time_part[:8]
                else:
                    date_part = str(timestamp)[:10] if timestamp else ""
                    time_part = str(timestamp)[11:19] if len(str(timestamp)) > 11 else ""
                
                action = str(log.get("action", "")).replace(",", ";")
                user = str(log.get("user", "Sistema")).replace(",", ";")
                details = str(log.get("details", "")).replace(",", ";")
                
                csv_lines.append(f"{date_part},{time_part},{action},{user},{details}")
            
            csv_content = "\n".join(csv_lines)
            
            # Converter para base64 e fazer download
            csv_b64 = base64.b64encode(csv_content.encode('utf-8-sig')).decode('utf-8')
            filename = f"logs_atividade_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
            
            self.is_exporting = False
            
            yield rx.call_script(
                f'''
                const link = document.createElement('a');
                link.href = 'data:text/csv;charset=utf-8;base64,{csv_b64}';
                link.download = '{filename}';
                link.click();
                '''
            )
            yield rx.toast.success(f"Logs exportados: {filename}")

        except Exception as e:
            self.is_exporting = False
            yield rx.toast.error(f"Erro ao exportar: {str(e)}")

    async def export_history_excel(self):
        """Exporta histórico completo como Excel"""
        self.is_exporting = True
        yield

        try:
            from ..utils.export_utils import generate_analyses_excel
            
            if not self.filtered_analyses:
                self.is_exporting = False
                yield rx.toast.warning("Nenhuma análise para exportar")
                return
            
            # Gerar Excel
            excel_bytes = generate_analyses_excel(self.filtered_analyses)
            excel_b64 = base64.b64encode(excel_bytes).decode('utf-8')
            
            filename = f"historico_analises_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
            
            self.is_exporting = False
            
            yield rx.call_script(
                f'''
                const link = document.createElement('a');
                link.href = 'data:application/vnd.openxmlformats-officedocument.spreadsheetml.sheet;base64,{excel_b64}';
                link.download = '{filename}';
                link.click();
                '''
            )
            yield rx.toast.success(f"Histórico exportado: {filename}")

        except Exception as e:
            self.is_exporting = False
            yield rx.toast.error(f"Erro ao exportar: {str(e)}")

    async def export_history_pdf(self):
        """Exporta histórico como PDF"""
        self.is_exporting = True
        yield

        try:
            from ..utils.export_utils import generate_combined_pdf
            
            if not self.filtered_analyses:
                self.is_exporting = False
                yield rx.toast.warning("Nenhuma análise para exportar")
                return
            
            # Gerar PDF
            pdf_bytes = generate_combined_pdf(self.filtered_analyses)
            pdf_b64 = base64.b64encode(pdf_bytes).decode('utf-8')
            
            filename = f"historico_analises_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
            
            self.is_exporting = False
            
            yield rx.call_script(
                f'''
                const link = document.createElement('a');
                link.href = 'data:application/pdf;base64,{pdf_b64}';
                link.download = '{filename}';
                link.click();
                '''
            )
            yield rx.toast.success(f"PDF gerado: {filename}")

        except Exception as e:
            self.is_exporting = False
            yield rx.toast.error(f"Erro ao exportar: {str(e)}")

"""
ReportsState - Estado de Relatorios
Gerencia filtros, exportacao e paginacao.
"""
import reflex as rx
from typing import List, Dict, Any
from datetime import datetime
import base64
import logging
from .auth_state import AuthState

logger = logging.getLogger(__name__)


class ReportsState(AuthState):
    """Estado responsavel pelos relatorios"""

    # Filtros
    type_filter: str = "Todos os Tipos"
    date_filter: str = "Ultimo Mes"
    search_query: str = ""

    # Paginacao
    current_page: int = 1
    items_per_page: int = 6

    # Exportacao
    is_exporting: bool = False
    export_format: str = ""
    
    # Download
    download_data: str = ""
    download_filename: str = ""

    def set_type_filter(self, value: str):
        """Filtra por tipo"""
        self.type_filter = value
        self.current_page = 1

    def set_date_filter(self, value: str):
        """Filtra por data"""
        self.date_filter = value
        self.current_page = 1

    def set_search_query(self, value: str):
        """Busca por nome"""
        self.search_query = value
        self.current_page = 1

    def clear_filters(self):
        """Limpa todos os filtros"""
        self.type_filter = "Todos os Tipos"
        self.date_filter = "Ultimo Mes"
        self.search_query = ""
        self.current_page = 1

    def next_page(self):
        """Vai para proxima pagina"""
        self.current_page += 1

    def prev_page(self):
        """Vai para pagina anterior"""
        if self.current_page > 1:
            self.current_page -= 1

    def go_to_page(self, page: int):
        """Vai para pagina especifica"""
        self.current_page = page

    async def _get_saved_analyses(self) -> List[Dict[str, Any]]:
        """Busca todas as análises salvas"""
        from ..services.local_storage import local_storage
        try:
            tenant_id = self.current_user.tenant_id if self.current_user else ""
            analyses = local_storage.get_saved_analyses(tenant_id, limit=500)
            return analyses
        except Exception as e:
            logger.error(f"Erro ao buscar analises: {e}")
            return []

    async def export_all_pdf(self):
        """Exporta todos como PDF"""
        self.is_exporting = True
        self.export_format = "PDF"
        yield

        try:
            from ..utils.export_utils import generate_combined_pdf
            
            # Buscar análises
            analyses = await self._get_saved_analyses()
            
            if not analyses:
                self.is_exporting = False
                yield rx.toast.warning("Nenhuma análise para exportar")
                return
            
            # Gerar PDF
            pdf_bytes = generate_combined_pdf(analyses)
            
            # Converter para base64 para download
            pdf_b64 = base64.b64encode(pdf_bytes).decode('utf-8')
            
            # Nome do arquivo
            filename = f"relatorios_labbridge_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
            
            self.is_exporting = False
            
            # Trigger download via JavaScript
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
            logger.error(f"Erro ao exportar PDF: {e}")
            yield rx.toast.error(f"Erro: {str(e)}")

    async def export_all_csv(self):
        """Exporta todos como CSV"""
        self.is_exporting = True
        self.export_format = "CSV"
        yield

        try:
            from ..utils.export_utils import generate_analyses_csv
            
            # Buscar análises
            analyses = await self._get_saved_analyses()
            
            if not analyses:
                self.is_exporting = False
                yield rx.toast.warning("Nenhuma análise para exportar")
                return
            
            # Gerar CSV
            csv_content = generate_analyses_csv(analyses)
            
            # Converter para base64
            csv_b64 = base64.b64encode(csv_content.encode('utf-8-sig')).decode('utf-8')
            
            # Nome do arquivo
            filename = f"relatorios_labbridge_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
            
            self.is_exporting = False
            
            # Trigger download
            yield rx.call_script(
                f'''
                const link = document.createElement('a');
                link.href = 'data:text/csv;charset=utf-8;base64,{csv_b64}';
                link.download = '{filename}';
                link.click();
                '''
            )
            yield rx.toast.success(f"CSV gerado: {filename}")

        except Exception as e:
            self.is_exporting = False
            logger.error(f"Erro ao exportar CSV: {e}")
            yield rx.toast.error(f"Erro: {str(e)}")

    async def export_all_excel(self):
        """Exporta todos como Excel"""
        self.is_exporting = True
        self.export_format = "Excel"
        yield

        try:
            from ..utils.export_utils import generate_analyses_excel
            
            # Buscar análises
            analyses = await self._get_saved_analyses()
            
            if not analyses:
                self.is_exporting = False
                yield rx.toast.warning("Nenhuma análise para exportar")
                return
            
            # Gerar Excel
            excel_bytes = generate_analyses_excel(analyses)
            
            # Converter para base64
            excel_b64 = base64.b64encode(excel_bytes).decode('utf-8')
            
            # Nome do arquivo
            filename = f"relatorios_labbridge_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
            
            self.is_exporting = False
            
            # Trigger download
            yield rx.call_script(
                f'''
                const link = document.createElement('a');
                link.href = 'data:application/vnd.openxmlformats-officedocument.spreadsheetml.sheet;base64,{excel_b64}';
                link.download = '{filename}';
                link.click();
                '''
            )
            yield rx.toast.success(f"Excel gerado: {filename}")

        except Exception as e:
            self.is_exporting = False
            logger.error(f"Erro ao exportar Excel: {e}")
            yield rx.toast.error(f"Erro: {str(e)}")

    @rx.var
    def can_go_prev(self) -> bool:
        return self.current_page > 1

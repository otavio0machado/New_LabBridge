"""
SavedAnalysisRepository - O Arquivista
Gerencia a persistência de análises salvas no Supabase seguindo o padrão Repository.
Com fallback para SQLite local quando Supabase não está disponível.
"""
from typing import Dict, Any, List, Optional
from datetime import date
from ..services.supabase_client import supabase
from ..services.local_storage import local_storage
from ..schemas.analysis_schemas import SavedAnalysisCreate, AnalysisItemCreate, analysis_to_dict


class SavedAnalysisRepository:
    """Repository para operações de Análises Salvas"""

    table_name = "saved_analyses"
    items_table = "analysis_items"

    @staticmethod
    def _use_local(tenant_id: str = "") -> bool:
        """Determina se deve usar armazenamento local"""
        # Usar local se: não há Supabase OU tenant é 'local'
        return not supabase or tenant_id == "local"

    @staticmethod
    def create(data: SavedAnalysisCreate) -> Optional[Dict[str, Any]]:
        """
        Cria uma nova análise salva.
        Valida dados com Pydantic antes de persistir.
        """
        tenant_id = data.tenant_id or "local"

        # Usar armazenamento local se necessário
        if SavedAnalysisRepository._use_local(tenant_id):
            db_data = analysis_to_dict(data)
            success, result, error = local_storage.create_analysis(db_data)
            if success:
                print(f"✅ Análise '{data.analysis_name}' salva localmente!")
                return result
            print(f"❌ Erro ao salvar análise local: {error}")
            return None

        try:
            # Validar e converter para dict
            db_data = analysis_to_dict(data)

            # Calcular diferença
            db_data['difference'] = db_data.get('compulab_total', 0) - db_data.get('simus_total', 0)

            response = supabase.table(SavedAnalysisRepository.table_name).insert(db_data).execute()

            if response.data:
                print(f"✅ Análise '{data.analysis_name}' salva com sucesso!")
                return response.data[0]
            return None

        except Exception as e:
            print(f"❌ Erro ao salvar análise: {e}")
            return None

    @staticmethod
    def get_all(tenant_id: str, limit: int = 50, order_by: str = "analysis_date") -> List[Dict[str, Any]]:
        """Retorna todas as análises salvas, ordenadas por data."""
        if not tenant_id:
            return []

        # Usar armazenamento local se necessário
        if SavedAnalysisRepository._use_local(tenant_id):
            return local_storage.get_saved_analyses(tenant_id, limit)

        try:
            response = supabase.table(SavedAnalysisRepository.table_name)\
                .select("id, analysis_name, analysis_date, compulab_total, simus_total, difference, missing_patients_count, missing_exams_count, divergences_count, status, created_at, analysis_report_url")\
                .eq("tenant_id", tenant_id)\
                .order(order_by, desc=True)\
                .limit(limit)\
                .execute()
            return response.data or []
        except Exception as e:
            print(f"Erro ao buscar análises: {e}")
            # Fallback para local em caso de erro
            return local_storage.get_saved_analyses(tenant_id, limit)

    @staticmethod
    def get_by_id(analysis_id: str) -> Optional[Dict[str, Any]]:
        """Retorna uma análise pelo ID com todos os detalhes."""
        # Tentar local primeiro (pode ser uma análise local)
        local_result = local_storage.get_analysis_by_id(analysis_id)
        if local_result:
            return local_result

        if not supabase:
            return None

        try:
            response = supabase.table(SavedAnalysisRepository.table_name)\
                .select("*")\
                .eq("id", analysis_id)\
                .single()\
                .execute()
            return response.data
        except Exception as e:
            print(f"Erro ao buscar análise {analysis_id}: {e}")
            return None

    @staticmethod
    def get_by_name_and_date(name: str, analysis_date: date) -> Optional[Dict[str, Any]]:
        """Busca análise por nome e data (único)."""
        if not supabase:
            return None

        try:
            response = supabase.table(SavedAnalysisRepository.table_name)\
                .select("*")\
                .eq("analysis_name", name)\
                .eq("analysis_date", analysis_date.isoformat())\
                .execute()

            if response.data:
                return response.data[0]
            return None
        except Exception as e:
            print(f"Erro ao buscar análise '{name}' em {analysis_date}: {e}")
            return None

    @staticmethod
    def search(tenant_id: str, query: str, limit: int = 20) -> List[Dict[str, Any]]:
        """Busca análises por nome (pesquisa parcial)."""
        # Usar armazenamento local se necessário
        if SavedAnalysisRepository._use_local(tenant_id):
            return local_storage.search_analyses(tenant_id, query, limit)

        try:
            response = supabase.table(SavedAnalysisRepository.table_name)\
                .select("id, analysis_name, analysis_date, compulab_total, simus_total, status")\
                .eq("tenant_id", tenant_id)\
                .ilike("analysis_name", f"%{query}%")\
                .order("analysis_date", desc=True)\
                .limit(limit)\
                .execute()
            return response.data or []
        except Exception as e:
            print(f"Erro na busca: {e}")
            return local_storage.search_analyses(tenant_id, query, limit)

    @staticmethod
    def update(analysis_id: str, data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Atualiza uma análise existente."""
        if not supabase:
            return None

        try:
            # Converter date se presente
            if 'analysis_date' in data and isinstance(data['analysis_date'], date):
                data['analysis_date'] = data['analysis_date'].isoformat()

            response = supabase.table(SavedAnalysisRepository.table_name)\
                .update(data)\
                .eq("id", analysis_id)\
                .execute()

            if response.data:
                return response.data[0]
            return None
        except Exception as e:
            print(f"Erro ao atualizar análise {analysis_id}: {e}")
            return None

    @staticmethod
    def delete(analysis_id: str) -> bool:
        """Deleta uma análise e seus itens (cascade)."""
        # Tentar deletar localmente primeiro
        success, _ = local_storage.delete_analysis(analysis_id)
        if success:
            return True

        if not supabase:
            return False

        try:
            # Items são deletados automaticamente via ON DELETE CASCADE
            response = supabase.table(SavedAnalysisRepository.table_name)\
                .delete()\
                .eq("id", analysis_id)\
                .execute()
            return bool(response.data)
        except Exception as e:
            print(f"Erro ao deletar análise {analysis_id}: {e}")
            return False

    @staticmethod
    def archive(analysis_id: str) -> bool:
        """Arquiva uma análise (soft delete)."""
        result = SavedAnalysisRepository.update(analysis_id, {"status": "archived"})
        return result is not None

    # ===== Métodos para Items de Análise =====

    @staticmethod
    def add_items(analysis_id: str, items: List[AnalysisItemCreate], use_local: bool = False) -> int:
        """Adiciona múltiplos itens a uma análise. Retorna quantidade inserida."""
        if not items:
            return 0

        # Usar armazenamento local se necessário
        if use_local or not supabase:
            items_data = [
                {
                    "item_type": item.item_type,
                    "patient_name": item.patient_name,
                    "exam_name": item.exam_name,
                    "compulab_value": item.compulab_value,
                    "simus_value": item.simus_value,
                    "difference": item.difference,
                    "exams_count": item.exams_count,
                }
                for item in items
            ]
            return local_storage.add_analysis_items(analysis_id, items_data)

        try:
            data_list = []
            for item in items:
                item_dict = item.dict(exclude_none=True)
                item_dict['analysis_id'] = analysis_id
                data_list.append(item_dict)

            response = supabase.table(SavedAnalysisRepository.items_table)\
                .insert(data_list)\
                .execute()

            return len(response.data) if response.data else 0
        except Exception as e:
            print(f"Erro ao adicionar itens: {e}")
            return 0

    @staticmethod
    def get_items(analysis_id: str, item_type: Optional[str] = None) -> List[Dict[str, Any]]:
        """Retorna itens de uma análise, opcionalmente filtrados por tipo."""
        # Tentar local primeiro
        local_items = local_storage.get_analysis_items(analysis_id, item_type)
        if local_items:
            return local_items

        if not supabase:
            return []

        try:
            query = supabase.table(SavedAnalysisRepository.items_table)\
                .select("*")\
                .eq("analysis_id", analysis_id)

            if item_type:
                query = query.eq("item_type", item_type)

            response = query.order("created_at").execute()
            return response.data or []
        except Exception as e:
            print(f"Erro ao buscar itens: {e}")
            return []

    @staticmethod
    def update_item_resolution(item_id: str, is_resolved: bool, notes: str = "") -> bool:
        """Atualiza status de resolução de um item."""
        if not supabase:
            return False

        try:
            response = supabase.table(SavedAnalysisRepository.items_table)\
                .update({"is_resolved": is_resolved, "resolution_notes": notes})\
                .eq("id", item_id)\
                .execute()
            return bool(response.data)
        except Exception as e:
            print(f"Erro ao atualizar item {item_id}: {e}")
            return False

    # ===== Métodos de Relatórios =====

    @staticmethod
    def get_monthly_summary(tenant_id: str, year: int, month: int) -> Optional[Dict[str, Any]]:
        """Retorna resumo das análises de um mês específico."""
        # Usar armazenamento local se necessário
        if SavedAnalysisRepository._use_local(tenant_id):
            return local_storage.get_monthly_summary(tenant_id, year, month)

        try:
            start_date = f"{year}-{month:02d}-01"
            if month == 12:
                end_date = f"{year + 1}-01-01"
            else:
                end_date = f"{year}-{month + 1:02d}-01"

            response = supabase.table(SavedAnalysisRepository.table_name)\
                .select("id, analysis_name, analysis_date, compulab_total, simus_total, difference")\
                .eq("tenant_id", tenant_id)\
                .gte("analysis_date", start_date)\
                .lt("analysis_date", end_date)\
                .order("analysis_date")\
                .execute()

            if not response.data:
                return local_storage.get_monthly_summary(tenant_id, year, month)

            # Calcular totais
            total_compulab = sum(a.get('compulab_total', 0) or 0 for a in response.data)
            total_simus = sum(a.get('simus_total', 0) or 0 for a in response.data)

            return {
                "analyses": response.data,
                "count": len(response.data),
                "total_compulab": total_compulab,
                "total_simus": total_simus,
                "total_difference": total_compulab - total_simus
            }
        except Exception as e:
            print(f"Erro ao gerar resumo mensal: {e}")
            return local_storage.get_monthly_summary(tenant_id, year, month)

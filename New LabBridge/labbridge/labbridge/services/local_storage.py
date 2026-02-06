"""
LocalStorage - Serviço de persistência local com SQLite
Permite funcionamento offline e fácil migração para backend real
"""
import json
import logging
import sqlite3
from pathlib import Path
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional, Tuple
import secrets

logger = logging.getLogger(__name__)


class LocalStorage:
    """Serviço de armazenamento local SQLite para dados de equipe e integrações"""
    
    _instance = None
    _db_path: Path = None
    _conn: sqlite3.Connection = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialize()
        return cls._instance
    
    def _initialize(self):
        """Inicializa banco de dados SQLite"""
        # Caminho do banco de dados na pasta do projeto
        base_path = Path(__file__).parent.parent
        self._db_path = base_path / "data" / "labbridge_local.db"
        
        # Criar diretório se não existir
        self._db_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Conectar e criar tabelas
        self._conn = sqlite3.connect(str(self._db_path), check_same_thread=False)
        self._conn.row_factory = sqlite3.Row
        self._create_tables()
        self._seed_initial_data()
    
    def _create_tables(self):
        """Cria tabelas necessárias"""
        cursor = self._conn.cursor()
        
        # Tabela de membros da equipe
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS team_members (
                id TEXT PRIMARY KEY,
                email TEXT NOT NULL,
                name TEXT NOT NULL,
                role TEXT DEFAULT 'viewer',
                status TEXT DEFAULT 'pending',
                tenant_id TEXT DEFAULT 'local',
                invited_by TEXT,
                last_active TEXT,
                created_at TEXT NOT NULL,
                UNIQUE(email, tenant_id)
            )
        """)
        
        # Tabela de convites
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS team_invites (
                id TEXT PRIMARY KEY,
                email TEXT NOT NULL,
                role TEXT DEFAULT 'viewer',
                tenant_id TEXT DEFAULT 'local',
                invited_by TEXT,
                token TEXT,
                message TEXT,
                status TEXT DEFAULT 'pending',
                expires_at TEXT,
                created_at TEXT NOT NULL
            )
        """)
        
        # Tabela de integrações
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS integrations (
                id TEXT PRIMARY KEY,
                name TEXT NOT NULL,
                description TEXT,
                category TEXT,
                icon TEXT DEFAULT '🔌',
                status TEXT DEFAULT 'inactive',
                tenant_id TEXT DEFAULT 'local',
                config TEXT DEFAULT '{}',
                credentials TEXT DEFAULT '{}',
                last_sync TEXT,
                last_error TEXT,
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL
            )
        """)
        
        # Tabela de logs de integração
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS integration_logs (
                id TEXT PRIMARY KEY,
                integration_id TEXT NOT NULL,
                action TEXT NOT NULL,
                status TEXT NOT NULL,
                message TEXT,
                details TEXT DEFAULT '{}',
                created_at TEXT NOT NULL,
                FOREIGN KEY (integration_id) REFERENCES integrations(id)
            )
        """)

        # Tabela de configurações do usuário
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS user_settings (
                id TEXT PRIMARY KEY,
                tenant_id TEXT DEFAULT 'local',
                user_id TEXT DEFAULT 'local-admin',
                settings_name TEXT,
                lab_name TEXT,
                lab_cnpj TEXT,
                ignore_small_diff INTEGER DEFAULT 1,
                auto_detect_typos INTEGER DEFAULT 1,
                notify_email_analysis INTEGER DEFAULT 1,
                notify_email_divergence INTEGER DEFAULT 1,
                notify_email_reports INTEGER DEFAULT 0,
                notify_push_enabled INTEGER DEFAULT 1,
                notify_weekly_summary INTEGER DEFAULT 1,
                notify_team_activity INTEGER DEFAULT 0,
                two_factor_enabled INTEGER DEFAULT 0,
                session_timeout TEXT DEFAULT '30',
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL,
                UNIQUE(tenant_id, user_id)
            )
        """)

        # Tabela de análises salvas
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS saved_analyses (
                id TEXT PRIMARY KEY,
                tenant_id TEXT DEFAULT 'local',
                analysis_name TEXT NOT NULL,
                analysis_date TEXT NOT NULL,
                description TEXT,
                compulab_file_url TEXT,
                compulab_file_name TEXT,
                simus_file_url TEXT,
                simus_file_name TEXT,
                analysis_report_url TEXT,
                compulab_total REAL DEFAULT 0,
                simus_total REAL DEFAULT 0,
                difference REAL DEFAULT 0,
                missing_patients_count INTEGER DEFAULT 0,
                missing_patients_total REAL DEFAULT 0,
                missing_exams_count INTEGER DEFAULT 0,
                missing_exams_total REAL DEFAULT 0,
                divergences_count INTEGER DEFAULT 0,
                divergences_total REAL DEFAULT 0,
                extra_simus_count INTEGER DEFAULT 0,
                ai_summary TEXT,
                status TEXT DEFAULT 'completed',
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL
            )
        """)

        # Tabela de itens de análise
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS analysis_items (
                id TEXT PRIMARY KEY,
                analysis_id TEXT NOT NULL,
                item_type TEXT NOT NULL,
                patient_name TEXT,
                exam_name TEXT,
                compulab_value REAL,
                simus_value REAL,
                difference REAL,
                exams_count INTEGER,
                is_resolved INTEGER DEFAULT 0,
                resolution_notes TEXT,
                created_at TEXT NOT NULL,
                FOREIGN KEY (analysis_id) REFERENCES saved_analyses(id) ON DELETE CASCADE
            )
        """)

        # Tabela de logs de atividade
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS activity_logs (
                id TEXT PRIMARY KEY,
                tenant_id TEXT DEFAULT 'local',
                action TEXT NOT NULL,
                user TEXT DEFAULT 'Sistema',
                details TEXT,
                entity_type TEXT,
                entity_id TEXT,
                created_at TEXT NOT NULL
            )
        """)

        # Tabela de notificações in-app
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS notifications (
                id TEXT PRIMARY KEY,
                tenant_id TEXT DEFAULT 'local',
                title TEXT NOT NULL,
                message TEXT NOT NULL,
                type TEXT DEFAULT 'info',
                action_url TEXT,
                read INTEGER DEFAULT 0,
                created_at TEXT NOT NULL
            )
        """)

        self._conn.commit()
    
    def _seed_initial_data(self):
        """Insere dados iniciais se o banco estiver vazio"""
        cursor = self._conn.cursor()
        
        # Verificar se já tem dados
        cursor.execute("SELECT COUNT(*) FROM team_members")
        if cursor.fetchone()[0] == 0:
            self._seed_team_members()
        
        cursor.execute("SELECT COUNT(*) FROM integrations")
        if cursor.fetchone()[0] == 0:
            self._seed_integrations()
    
    def _seed_team_members(self):
        """Insere membros iniciais da equipe"""
        now = datetime.utcnow()
        members = [
            {
                "id": "1",
                "email": "admin@labbridge.com",
                "name": "Admin Principal",
                "role": "admin_global",
                "status": "active",
                "last_active": now.isoformat(),
                "created_at": "2024-01-01T00:00:00"
            },
            {
                "id": "2",
                "email": "joao@laboratorio.com",
                "name": "Dr. João Silva",
                "role": "admin_lab",
                "status": "active",
                "last_active": (now - timedelta(minutes=5)).isoformat(),
                "created_at": "2024-01-15T00:00:00"
            },
            {
                "id": "3",
                "email": "ana@laboratorio.com",
                "name": "Ana Costa",
                "role": "analyst",
                "status": "active",
                "last_active": (now - timedelta(hours=1)).isoformat(),
                "created_at": "2024-02-01T00:00:00"
            },
            {
                "id": "4",
                "email": "carlos@laboratorio.com",
                "name": "Carlos Souza",
                "role": "analyst",
                "status": "active",
                "last_active": (now - timedelta(hours=2)).isoformat(),
                "created_at": "2024-02-15T00:00:00"
            },
            {
                "id": "5",
                "email": "maria@laboratorio.com",
                "name": "Maria Santos",
                "role": "viewer",
                "status": "active",
                "last_active": (now - timedelta(days=1)).isoformat(),
                "created_at": "2024-03-01T00:00:00"
            },
            {
                "id": "6",
                "email": "pedro@laboratorio.com",
                "name": "Pedro Lima",
                "role": "viewer",
                "status": "active",
                "last_active": (now - timedelta(days=3)).isoformat(),
                "created_at": "2024-03-15T00:00:00"
            },
            {
                "id": "7",
                "email": "julia@laboratorio.com",
                "name": "Julia Oliveira",
                "role": "analyst",
                "status": "pending",
                "last_active": None,
                "created_at": "2024-04-01T00:00:00"
            },
            {
                "id": "8",
                "email": "lucas@laboratorio.com",
                "name": "Lucas Mendes",
                "role": "viewer",
                "status": "pending",
                "last_active": None,
                "created_at": "2024-04-05T00:00:00"
            },
        ]
        
        cursor = self._conn.cursor()
        for m in members:
            cursor.execute("""
                INSERT INTO team_members (id, email, name, role, status, tenant_id, last_active, created_at)
                VALUES (?, ?, ?, ?, ?, 'local', ?, ?)
            """, (m["id"], m["email"], m["name"], m["role"], m["status"], m["last_active"], m["created_at"]))
        
        self._conn.commit()
    
    def _seed_integrations(self):
        """Insere integrações iniciais"""
        now = datetime.utcnow()
        integrations = [
            {
                "id": "1",
                "name": "Shift LIS",
                "description": "Sistema de Gestão Laboratorial",
                "category": "lis",
                "icon": "🔬",
                "status": "active",
                "last_sync": now.isoformat(),
            },
            {
                "id": "2",
                "name": "Matrix",
                "description": "Integração via API HL7/FHIR",
                "category": "lis",
                "icon": "🧬",
                "status": "inactive",
            },
            {
                "id": "3",
                "name": "Concent",
                "description": "Faturamento TISS e gestão de glosas",
                "category": "billing",
                "icon": "💰",
                "status": "error",
                "last_error": "Credenciais expiradas",
            },
            {
                "id": "4",
                "name": "Portal TISS",
                "description": "Envio automático de guias",
                "category": "billing",
                "icon": "📋",
                "status": "inactive",
            },
            {
                "id": "5",
                "name": "Google Drive",
                "description": "Backup e exportação de relatórios",
                "category": "storage",
                "icon": "📁",
                "status": "active",
                "last_sync": now.isoformat(),
            },
            {
                "id": "6",
                "name": "WhatsApp Business",
                "description": "Envio automatizado de resultados",
                "category": "communication",
                "icon": "💬",
                "status": "active",
                "last_sync": now.isoformat(),
            },
        ]
        
        cursor = self._conn.cursor()
        for i in integrations:
            cursor.execute("""
                INSERT INTO integrations (id, name, description, category, icon, status, tenant_id, last_sync, last_error, created_at, updated_at)
                VALUES (?, ?, ?, ?, ?, ?, 'local', ?, ?, ?, ?)
            """, (
                i["id"], i["name"], i["description"], i["category"], i["icon"], 
                i["status"], i.get("last_sync"), i.get("last_error"),
                now.isoformat(), now.isoformat()
            ))
        
        self._conn.commit()
    
    # =========================================================================
    # TEAM MEMBERS CRUD
    # =========================================================================
    
    def get_team_members(self, tenant_id: str = "local") -> List[Dict[str, Any]]:
        """Lista todos os membros da equipe"""
        cursor = self._conn.cursor()
        cursor.execute(
            "SELECT * FROM team_members WHERE tenant_id = ? ORDER BY created_at DESC",
            (tenant_id,)
        )
        return [dict(row) for row in cursor.fetchall()]
    
    def get_member_by_id(self, member_id: str) -> Optional[Dict[str, Any]]:
        """Busca membro por ID"""
        cursor = self._conn.cursor()
        cursor.execute("SELECT * FROM team_members WHERE id = ?", (member_id,))
        row = cursor.fetchone()
        return dict(row) if row else None
    
    def get_member_by_email(self, email: str, tenant_id: str = "local") -> Optional[Dict[str, Any]]:
        """Busca membro por email"""
        cursor = self._conn.cursor()
        cursor.execute(
            "SELECT * FROM team_members WHERE email = ? AND tenant_id = ?",
            (email, tenant_id)
        )
        row = cursor.fetchone()
        return dict(row) if row else None
    
    def create_member(self, data: Dict[str, Any]) -> Tuple[bool, Optional[Dict[str, Any]], str]:
        """Cria novo membro"""
        try:
            # Verificar se já existe
            existing = self.get_member_by_email(data["email"], data.get("tenant_id", "local"))
            if existing:
                return False, None, "Este email já está cadastrado na equipe"
            
            # Gerar ID único
            member_id = str(int(datetime.utcnow().timestamp() * 1000))
            now = datetime.utcnow().isoformat()
            
            cursor = self._conn.cursor()
            cursor.execute("""
                INSERT INTO team_members (id, email, name, role, status, tenant_id, invited_by, created_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                member_id,
                data["email"],
                data.get("name", data["email"].split("@")[0]),
                data.get("role", "viewer"),
                data.get("status", "pending"),
                data.get("tenant_id", "local"),
                data.get("invited_by", ""),
                now
            ))
            self._conn.commit()
            
            return True, self.get_member_by_id(member_id), ""
        except Exception as e:
            return False, None, f"Erro ao criar membro: {str(e)}"
    
    def update_member(self, member_id: str, data: Dict[str, Any]) -> Tuple[bool, str]:
        """Atualiza membro"""
        try:
            updates = []
            values = []
            
            for field in ["name", "role", "status", "last_active"]:
                if field in data:
                    updates.append(f"{field} = ?")
                    values.append(data[field])
            
            if not updates:
                return True, ""
            
            values.append(member_id)
            cursor = self._conn.cursor()
            cursor.execute(
                f"UPDATE team_members SET {', '.join(updates)} WHERE id = ?",
                values
            )
            self._conn.commit()
            
            return True, ""
        except Exception as e:
            return False, f"Erro ao atualizar membro: {str(e)}"
    
    def delete_member(self, member_id: str) -> Tuple[bool, str]:
        """Remove membro"""
        try:
            cursor = self._conn.cursor()
            cursor.execute("DELETE FROM team_members WHERE id = ?", (member_id,))
            self._conn.commit()
            return True, ""
        except Exception as e:
            return False, f"Erro ao remover membro: {str(e)}"
    
    # =========================================================================
    # TEAM INVITES
    # =========================================================================
    
    def create_invite(
        self, 
        email: str, 
        role: str, 
        tenant_id: str,
        invited_by: str,
        message: str = ""
    ) -> Tuple[bool, Optional[Dict[str, Any]], str]:
        """Cria convite para novo membro"""
        try:
            # Verificar se já existe membro
            existing = self.get_member_by_email(email, tenant_id)
            if existing:
                return False, None, "Este email já está na equipe"
            
            invite_id = str(int(datetime.utcnow().timestamp() * 1000))
            token = secrets.token_urlsafe(32)
            now = datetime.utcnow()
            expires_at = (now + timedelta(days=7)).isoformat()
            
            cursor = self._conn.cursor()
            cursor.execute("""
                INSERT INTO team_invites (id, email, role, tenant_id, invited_by, token, message, status, expires_at, created_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, 'pending', ?, ?)
            """, (invite_id, email, role, tenant_id, invited_by, token, message, expires_at, now.isoformat()))
            
            # Criar membro com status pending
            self.create_member({
                "email": email,
                "name": email.split("@")[0].title(),
                "role": role,
                "status": "pending",
                "tenant_id": tenant_id,
                "invited_by": invited_by
            })
            
            self._conn.commit()
            
            cursor.execute("SELECT * FROM team_invites WHERE id = ?", (invite_id,))
            row = cursor.fetchone()
            return True, dict(row) if row else None, ""
        except Exception as e:
            return False, None, f"Erro ao criar convite: {str(e)}"
    
    def resend_invite(self, member_id: str) -> Tuple[bool, str]:
        """Reenvia convite (simulado)"""
        member = self.get_member_by_id(member_id)
        if not member:
            return False, "Membro não encontrado"
        if member["status"] != "pending":
            return False, "Membro não está pendente"
        return True, f"Convite reenviado para {member['email']}"
    
    # =========================================================================
    # INTEGRATIONS CRUD
    # =========================================================================
    
    def get_integrations(self, tenant_id: str = "local") -> List[Dict[str, Any]]:
        """Lista todas as integrações"""
        cursor = self._conn.cursor()
        cursor.execute(
            "SELECT * FROM integrations WHERE tenant_id = ? ORDER BY created_at DESC",
            (tenant_id,)
        )
        rows = cursor.fetchall()
        result = []
        for row in rows:
            d = dict(row)
            # Parse JSON fields
            d["config"] = json.loads(d.get("config") or "{}")
            d["credentials"] = json.loads(d.get("credentials") or "{}")
            result.append(d)
        return result
    
    def get_integration_by_id(self, integration_id: str) -> Optional[Dict[str, Any]]:
        """Busca integração por ID"""
        cursor = self._conn.cursor()
        cursor.execute("SELECT * FROM integrations WHERE id = ?", (integration_id,))
        row = cursor.fetchone()
        if row:
            d = dict(row)
            d["config"] = json.loads(d.get("config") or "{}")
            d["credentials"] = json.loads(d.get("credentials") or "{}")
            return d
        return None
    
    def create_integration(self, data: Dict[str, Any]) -> Tuple[bool, Optional[Dict[str, Any]], str]:
        """Cria nova integração"""
        try:
            integration_id = str(int(datetime.utcnow().timestamp() * 1000))
            now = datetime.utcnow().isoformat()
            
            cursor = self._conn.cursor()
            cursor.execute("""
                INSERT INTO integrations (id, name, description, category, icon, status, tenant_id, config, credentials, created_at, updated_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                integration_id,
                data["name"],
                data.get("description", ""),
                data.get("category", "other"),
                data.get("icon", "🔌"),
                "inactive",
                data.get("tenant_id", "local"),
                json.dumps(data.get("config", {})),
                json.dumps({}),
                now,
                now
            ))
            self._conn.commit()
            
            return True, self.get_integration_by_id(integration_id), ""
        except Exception as e:
            return False, None, f"Erro ao criar integração: {str(e)}"
    
    def update_integration(self, integration_id: str, data: Dict[str, Any]) -> Tuple[bool, str]:
        """Atualiza integração"""
        try:
            updates = ["updated_at = ?"]
            values = [datetime.utcnow().isoformat()]
            
            for field in ["name", "description", "status", "last_sync", "last_error"]:
                if field in data:
                    updates.append(f"{field} = ?")
                    values.append(data[field])
            
            if "config" in data:
                updates.append("config = ?")
                values.append(json.dumps(data["config"]))
            
            if "credentials" in data:
                updates.append("credentials = ?")
                values.append(json.dumps(data["credentials"]))
            
            values.append(integration_id)
            cursor = self._conn.cursor()
            cursor.execute(
                f"UPDATE integrations SET {', '.join(updates)} WHERE id = ?",
                values
            )
            self._conn.commit()
            
            return True, ""
        except Exception as e:
            return False, f"Erro ao atualizar integração: {str(e)}"
    
    def delete_integration(self, integration_id: str) -> Tuple[bool, str]:
        """Remove integração"""
        try:
            cursor = self._conn.cursor()
            cursor.execute("DELETE FROM integrations WHERE id = ?", (integration_id,))
            self._conn.commit()
            return True, ""
        except Exception as e:
            return False, f"Erro ao remover integração: {str(e)}"
    
    def toggle_integration(self, integration_id: str, active: bool) -> Tuple[bool, str]:
        """Ativa/desativa integração"""
        new_status = "active" if active else "inactive"
        update_data = {"status": new_status}
        if active:
            update_data["last_sync"] = datetime.utcnow().isoformat()
            update_data["last_error"] = None
        return self.update_integration(integration_id, update_data)
    
    def sync_integration(self, integration_id: str) -> Tuple[bool, str]:
        """Simula sincronização de integração"""
        integration = self.get_integration_by_id(integration_id)
        if not integration:
            return False, "Integração não encontrada"
        
        if integration["status"] != "active":
            return False, "Integração não está ativa"
        
        # Simular sync bem sucedido
        self.update_integration(integration_id, {
            "last_sync": datetime.utcnow().isoformat(),
            "last_error": None
        })
        
        # Log
        self.log_integration_activity(
            integration_id, "sync", "success", 
            f"Sincronização de {integration['name']} concluída"
        )
        
        return True, f"Sincronização de {integration['name']} concluída com sucesso"
    
    def test_connection(self, integration_id: str) -> Tuple[bool, str]:
        """Simula teste de conexão"""
        integration = self.get_integration_by_id(integration_id)
        if not integration:
            return False, "Integração não encontrada"
        
        # Simular teste
        if integration["status"] == "error":
            return False, f"Falha na conexão com {integration['name']}: {integration.get('last_error', 'Erro desconhecido')}"
        
        return True, f"Conexão com {integration['name']} estabelecida com sucesso"
    
    # =========================================================================
    # INTEGRATION LOGS
    # =========================================================================
    
    def log_integration_activity(
        self,
        integration_id: str,
        action: str,
        status: str,
        message: str,
        details: Dict[str, Any] = None
    ):
        """Registra log de atividade"""
        try:
            log_id = str(int(datetime.utcnow().timestamp() * 1000000))
            cursor = self._conn.cursor()
            cursor.execute("""
                INSERT INTO integration_logs (id, integration_id, action, status, message, details, created_at)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (
                log_id, integration_id, action, status, message,
                json.dumps(details or {}), datetime.utcnow().isoformat()
            ))
            self._conn.commit()
        except Exception as e:
            logger.error(f"Erro ao registrar log: {e}")
    
    def get_integration_logs(self, integration_id: str, limit: int = 50) -> List[Dict[str, Any]]:
        """Retorna logs de uma integração"""
        cursor = self._conn.cursor()
        cursor.execute("""
            SELECT * FROM integration_logs 
            WHERE integration_id = ? 
            ORDER BY created_at DESC 
            LIMIT ?
        """, (integration_id, limit))
        
        return [dict(row) for row in cursor.fetchall()]
    
    # =========================================================================
    # STATISTICS
    # =========================================================================
    
    def get_team_stats(self, tenant_id: str = "local") -> Dict[str, int]:
        """Estatísticas da equipe"""
        members = self.get_team_members(tenant_id)
        return {
            "total": len(members),
            "active": sum(1 for m in members if m.get("status") == "active"),
            "pending": sum(1 for m in members if m.get("status") == "pending"),
            "admins": sum(1 for m in members if m.get("role") in ["admin_global", "admin_lab"]),
        }
    
    def get_integration_stats(self, tenant_id: str = "local") -> Dict[str, int]:
        """Estatísticas das integrações"""
        integrations = self.get_integrations(tenant_id)
        return {
            "total": len(integrations),
            "active": sum(1 for i in integrations if i.get("status") == "active"),
            "inactive": sum(1 for i in integrations if i.get("status") == "inactive"),
            "error": sum(1 for i in integrations if i.get("status") == "error"),
        }

    # =========================================================================
    # SAVED ANALYSES CRUD
    # =========================================================================

    def get_saved_analyses(self, tenant_id: str = "local", limit: int = 50) -> List[Dict[str, Any]]:
        """Lista todas as análises salvas"""
        cursor = self._conn.cursor()
        cursor.execute("""
            SELECT * FROM saved_analyses
            WHERE tenant_id = ?
            ORDER BY analysis_date DESC, created_at DESC
            LIMIT ?
        """, (tenant_id, limit))

        results = []
        for row in cursor.fetchall():
            d = dict(row)
            # Formatar para compatibilidade com o frontend
            d["formatted_date"] = d.get("analysis_date", "")
            d["formatted_time"] = d.get("created_at", "")[:16].replace("T", " ") if d.get("created_at") else ""
            d["formatted_compulab"] = f"R$ {d.get('compulab_total', 0):,.2f}"
            d["formatted_simus"] = f"R$ {d.get('simus_total', 0):,.2f}"
            d["formatted_difference"] = f"R$ {d.get('difference', 0):,.2f}"
            results.append(d)
        return results

    def get_analysis_by_id(self, analysis_id: str) -> Optional[Dict[str, Any]]:
        """Busca análise por ID"""
        cursor = self._conn.cursor()
        cursor.execute("SELECT * FROM saved_analyses WHERE id = ?", (analysis_id,))
        row = cursor.fetchone()
        return dict(row) if row else None

    def create_analysis(self, data: Dict[str, Any]) -> Tuple[bool, Optional[Dict[str, Any]], str]:
        """Cria nova análise salva"""
        try:
            analysis_id = str(int(datetime.utcnow().timestamp() * 1000))
            now = datetime.utcnow().isoformat()

            # Calcular diferença
            compulab_total = data.get("compulab_total", 0) or 0
            simus_total = data.get("simus_total", 0) or 0
            difference = compulab_total - simus_total

            cursor = self._conn.cursor()
            cursor.execute("""
                INSERT INTO saved_analyses (
                    id, tenant_id, analysis_name, analysis_date, description,
                    compulab_file_url, compulab_file_name, simus_file_url, simus_file_name,
                    analysis_report_url, compulab_total, simus_total, difference,
                    missing_patients_count, missing_patients_total, missing_exams_count, missing_exams_total,
                    divergences_count, divergences_total, extra_simus_count,
                    ai_summary, status, created_at, updated_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                analysis_id,
                data.get("tenant_id", "local"),
                data.get("analysis_name", "Análise"),
                data.get("analysis_date", now[:10]),
                data.get("description", ""),
                data.get("compulab_file_url"),
                data.get("compulab_file_name"),
                data.get("simus_file_url"),
                data.get("simus_file_name"),
                data.get("analysis_report_url"),
                compulab_total,
                simus_total,
                difference,
                data.get("missing_patients_count", 0),
                data.get("missing_patients_total", 0),
                data.get("missing_exams_count", 0),
                data.get("missing_exams_total", 0),
                data.get("divergences_count", 0),
                data.get("divergences_total", 0),
                data.get("extra_simus_count", 0),
                data.get("ai_summary", ""),
                data.get("status", "completed"),
                now,
                now
            ))
            self._conn.commit()

            return True, {"id": analysis_id, **data}, ""
        except Exception as e:
            return False, None, f"Erro ao criar análise: {str(e)}"

    def add_analysis_items(self, analysis_id: str, items: List[Dict[str, Any]]) -> int:
        """Adiciona itens a uma análise"""
        if not items:
            return 0

        try:
            cursor = self._conn.cursor()
            now = datetime.utcnow().isoformat()
            count = 0

            for item in items:
                item_id = str(int(datetime.utcnow().timestamp() * 1000000) + count)
                cursor.execute("""
                    INSERT INTO analysis_items (
                        id, analysis_id, item_type, patient_name, exam_name,
                        compulab_value, simus_value, difference, exams_count,
                        is_resolved, resolution_notes, created_at
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    item_id,
                    analysis_id,
                    item.get("item_type", ""),
                    item.get("patient_name", ""),
                    item.get("exam_name", ""),
                    item.get("compulab_value"),
                    item.get("simus_value"),
                    item.get("difference"),
                    item.get("exams_count"),
                    1 if item.get("is_resolved") else 0,
                    item.get("resolution_notes", ""),
                    now
                ))
                count += 1

            self._conn.commit()
            return count
        except Exception as e:
            logger.error(f"Erro ao adicionar itens: {e}")
            return 0

    def get_analysis_items(self, analysis_id: str, item_type: str = None) -> List[Dict[str, Any]]:
        """Retorna itens de uma análise"""
        cursor = self._conn.cursor()

        if item_type:
            cursor.execute("""
                SELECT * FROM analysis_items
                WHERE analysis_id = ? AND item_type = ?
                ORDER BY created_at
            """, (analysis_id, item_type))
        else:
            cursor.execute("""
                SELECT * FROM analysis_items
                WHERE analysis_id = ?
                ORDER BY created_at
            """, (analysis_id,))

        return [dict(row) for row in cursor.fetchall()]

    def load_analysis_complete(self, analysis_id: str) -> Optional[Dict[str, Any]]:
        """Carrega análise completa com todos os itens"""
        analysis = self.get_analysis_by_id(analysis_id)
        if not analysis:
            return None

        analysis["missing_patients"] = self.get_analysis_items(analysis_id, "missing_patient")
        analysis["missing_exams"] = self.get_analysis_items(analysis_id, "missing_exam")
        analysis["divergences"] = self.get_analysis_items(analysis_id, "divergence")
        analysis["extra_simus"] = self.get_analysis_items(analysis_id, "extra_simus")

        return analysis

    def delete_analysis(self, analysis_id: str) -> Tuple[bool, str]:
        """Remove análise e seus itens"""
        try:
            cursor = self._conn.cursor()
            # Items são deletados automaticamente via CASCADE (se SQLite suportar)
            cursor.execute("DELETE FROM analysis_items WHERE analysis_id = ?", (analysis_id,))
            cursor.execute("DELETE FROM saved_analyses WHERE id = ?", (analysis_id,))
            self._conn.commit()
            return True, ""
        except Exception as e:
            return False, f"Erro ao remover análise: {str(e)}"

    def search_analyses(self, tenant_id: str, query: str, limit: int = 20) -> List[Dict[str, Any]]:
        """Busca análises por nome"""
        cursor = self._conn.cursor()
        cursor.execute("""
            SELECT * FROM saved_analyses
            WHERE tenant_id = ? AND analysis_name LIKE ?
            ORDER BY analysis_date DESC
            LIMIT ?
        """, (tenant_id, f"%{query}%", limit))

        results = []
        for row in cursor.fetchall():
            d = dict(row)
            d["formatted_date"] = d.get("analysis_date", "")
            d["formatted_compulab"] = f"R$ {d.get('compulab_total', 0):,.2f}"
            d["formatted_simus"] = f"R$ {d.get('simus_total', 0):,.2f}"
            results.append(d)
        return results

    def get_monthly_summary(self, tenant_id: str, year: int, month: int) -> Optional[Dict[str, Any]]:
        """Retorna resumo mensal das análises"""
        start_date = f"{year}-{month:02d}-01"
        if month == 12:
            end_date = f"{year + 1}-01-01"
        else:
            end_date = f"{year}-{month + 1:02d}-01"

        cursor = self._conn.cursor()
        cursor.execute("""
            SELECT * FROM saved_analyses
            WHERE tenant_id = ? AND analysis_date >= ? AND analysis_date < ?
            ORDER BY analysis_date
        """, (tenant_id, start_date, end_date))

        rows = [dict(row) for row in cursor.fetchall()]
        if not rows:
            return None

        total_compulab = sum(r.get("compulab_total", 0) or 0 for r in rows)
        total_simus = sum(r.get("simus_total", 0) or 0 for r in rows)

        return {
            "analyses": rows,
            "count": len(rows),
            "total_compulab": total_compulab,
            "total_simus": total_simus,
            "total_difference": total_compulab - total_simus
        }

    # =========================================================================
    # USER SETTINGS CRUD
    # =========================================================================

    def get_user_settings(self, tenant_id: str = "local", user_id: str = "local-admin") -> Optional[Dict[str, Any]]:
        """Retorna configurações do usuário"""
        cursor = self._conn.cursor()
        cursor.execute("""
            SELECT * FROM user_settings
            WHERE tenant_id = ? AND user_id = ?
        """, (tenant_id, user_id))
        row = cursor.fetchone()
        if row:
            d = dict(row)
            # Converter inteiros para booleanos
            d["ignore_small_diff"] = bool(d.get("ignore_small_diff", 1))
            d["auto_detect_typos"] = bool(d.get("auto_detect_typos", 1))
            d["notify_email_analysis"] = bool(d.get("notify_email_analysis", 1))
            d["notify_email_divergence"] = bool(d.get("notify_email_divergence", 1))
            d["notify_email_reports"] = bool(d.get("notify_email_reports", 0))
            d["notify_push_enabled"] = bool(d.get("notify_push_enabled", 1))
            d["notify_weekly_summary"] = bool(d.get("notify_weekly_summary", 1))
            d["notify_team_activity"] = bool(d.get("notify_team_activity", 0))
            d["two_factor_enabled"] = bool(d.get("two_factor_enabled", 0))
            return d
        return None

    def save_user_settings(self, data: Dict[str, Any]) -> Tuple[bool, str]:
        """Salva configurações do usuário"""
        try:
            tenant_id = data.get("tenant_id", "local")
            user_id = data.get("user_id", "local-admin")
            now = datetime.utcnow().isoformat()

            # Verificar se já existe
            existing = self.get_user_settings(tenant_id, user_id)

            cursor = self._conn.cursor()

            if existing:
                # Update
                cursor.execute("""
                    UPDATE user_settings SET
                        settings_name = ?,
                        lab_name = ?,
                        lab_cnpj = ?,
                        ignore_small_diff = ?,
                        auto_detect_typos = ?,
                        notify_email_analysis = ?,
                        notify_email_divergence = ?,
                        notify_email_reports = ?,
                        notify_push_enabled = ?,
                        notify_weekly_summary = ?,
                        notify_team_activity = ?,
                        two_factor_enabled = ?,
                        session_timeout = ?,
                        updated_at = ?
                    WHERE tenant_id = ? AND user_id = ?
                """, (
                    data.get("settings_name", ""),
                    data.get("lab_name", ""),
                    data.get("lab_cnpj", ""),
                    1 if data.get("ignore_small_diff", True) else 0,
                    1 if data.get("auto_detect_typos", True) else 0,
                    1 if data.get("notify_email_analysis", True) else 0,
                    1 if data.get("notify_email_divergence", True) else 0,
                    1 if data.get("notify_email_reports", False) else 0,
                    1 if data.get("notify_push_enabled", True) else 0,
                    1 if data.get("notify_weekly_summary", True) else 0,
                    1 if data.get("notify_team_activity", False) else 0,
                    1 if data.get("two_factor_enabled", False) else 0,
                    data.get("session_timeout", "30"),
                    now,
                    tenant_id,
                    user_id
                ))
            else:
                # Insert
                settings_id = str(int(datetime.utcnow().timestamp() * 1000))
                cursor.execute("""
                    INSERT INTO user_settings (
                        id, tenant_id, user_id, settings_name, lab_name, lab_cnpj,
                        ignore_small_diff, auto_detect_typos,
                        notify_email_analysis, notify_email_divergence, notify_email_reports,
                        notify_push_enabled, notify_weekly_summary, notify_team_activity,
                        two_factor_enabled, session_timeout, created_at, updated_at
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    settings_id,
                    tenant_id,
                    user_id,
                    data.get("settings_name", ""),
                    data.get("lab_name", ""),
                    data.get("lab_cnpj", ""),
                    1 if data.get("ignore_small_diff", True) else 0,
                    1 if data.get("auto_detect_typos", True) else 0,
                    1 if data.get("notify_email_analysis", True) else 0,
                    1 if data.get("notify_email_divergence", True) else 0,
                    1 if data.get("notify_email_reports", False) else 0,
                    1 if data.get("notify_push_enabled", True) else 0,
                    1 if data.get("notify_weekly_summary", True) else 0,
                    1 if data.get("notify_team_activity", False) else 0,
                    1 if data.get("two_factor_enabled", False) else 0,
                    data.get("session_timeout", "30"),
                    now,
                    now
                ))

            self._conn.commit()
            return True, ""
        except Exception as e:
            return False, f"Erro ao salvar configurações: {str(e)}"

    # =========================================================================
    # ACTIVITY LOGS CRUD
    # =========================================================================

    def add_activity_log(
        self, 
        tenant_id: str, 
        action: str, 
        details: str = "", 
        user: str = "Sistema",
        entity_type: str = None,
        entity_id: str = None
    ) -> bool:
        """Adiciona um log de atividade"""
        try:
            log_id = str(int(datetime.utcnow().timestamp() * 1000))
            now = datetime.utcnow().isoformat()
            
            cursor = self._conn.cursor()
            cursor.execute("""
                INSERT INTO activity_logs (id, tenant_id, action, user, details, entity_type, entity_id, created_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (log_id, tenant_id, action, user, details, entity_type, entity_id, now))
            
            self._conn.commit()
            return True
        except Exception as e:
            logger.error(f"Erro ao adicionar log: {e}")
            return False

    def get_activity_logs(self, tenant_id: str, limit: int = 50) -> List[Dict[str, Any]]:
        """Retorna logs de atividade"""
        cursor = self._conn.cursor()
        cursor.execute("""
            SELECT * FROM activity_logs
            WHERE tenant_id = ?
            ORDER BY created_at DESC
            LIMIT ?
        """, (tenant_id, limit))
        
        return [dict(row) for row in cursor.fetchall()]

    def get_activity_logs_by_entity(self, entity_type: str, entity_id: str, limit: int = 20) -> List[Dict[str, Any]]:
        """Retorna logs de uma entidade específica"""
        cursor = self._conn.cursor()
        cursor.execute("""
            SELECT * FROM activity_logs
            WHERE entity_type = ? AND entity_id = ?
            ORDER BY created_at DESC
            LIMIT ?
        """, (entity_type, entity_id, limit))
        
        return [dict(row) for row in cursor.fetchall()]

    def clear_old_logs(self, days: int = 90) -> int:
        """Remove logs antigos (mais de X dias)"""
        cutoff = (datetime.utcnow() - timedelta(days=days)).isoformat()
        
        cursor = self._conn.cursor()
        cursor.execute("""
            DELETE FROM activity_logs WHERE created_at < ?
        """, (cutoff,))
        
        deleted = cursor.rowcount
        self._conn.commit()
        return deleted

    # =========================================================================
    # NOTIFICATIONS CRUD
    # =========================================================================

    def add_notification(
        self,
        tenant_id: str,
        title: str,
        message: str,
        type: str = "info",
        action_url: str = None
    ) -> str:
        """Adiciona uma nova notificação"""
        try:
            notif_id = str(int(datetime.utcnow().timestamp() * 1000))
            now = datetime.utcnow().isoformat()
            
            cursor = self._conn.cursor()
            cursor.execute("""
                INSERT INTO notifications (id, tenant_id, title, message, type, action_url, read, created_at)
                VALUES (?, ?, ?, ?, ?, ?, 0, ?)
            """, (notif_id, tenant_id, title, message, type, action_url, now))
            
            self._conn.commit()
            return notif_id
        except Exception as e:
            logger.error(f"Erro ao adicionar notificacao: {e}")
            return None

    def get_notifications(self, tenant_id: str, limit: int = 50, unread_only: bool = False) -> List[Dict[str, Any]]:
        """Retorna notificações do tenant"""
        cursor = self._conn.cursor()
        
        if unread_only:
            cursor.execute("""
                SELECT * FROM notifications
                WHERE tenant_id = ? AND read = 0
                ORDER BY created_at DESC
                LIMIT ?
            """, (tenant_id, limit))
        else:
            cursor.execute("""
                SELECT * FROM notifications
                WHERE tenant_id = ?
                ORDER BY created_at DESC
                LIMIT ?
            """, (tenant_id, limit))
        
        return [dict(row) for row in cursor.fetchall()]

    def mark_notification_read(self, notification_id: str) -> bool:
        """Marca notificação como lida"""
        try:
            cursor = self._conn.cursor()
            cursor.execute("""
                UPDATE notifications SET read = 1 WHERE id = ?
            """, (notification_id,))
            
            self._conn.commit()
            return True
        except Exception as e:
            logger.error(f"Erro ao marcar notificacao: {e}")
            return False

    def mark_all_notifications_read(self, tenant_id: str) -> bool:
        """Marca todas notificações como lidas"""
        try:
            cursor = self._conn.cursor()
            cursor.execute("""
                UPDATE notifications SET read = 1 WHERE tenant_id = ?
            """, (tenant_id,))
            
            self._conn.commit()
            return True
        except Exception as e:
            logger.error(f"Erro ao marcar notificacoes: {e}")
            return False

    def clear_notifications(self, tenant_id: str) -> bool:
        """Limpa todas notificações do tenant"""
        try:
            cursor = self._conn.cursor()
            cursor.execute("""
                DELETE FROM notifications WHERE tenant_id = ?
            """, (tenant_id,))
            
            self._conn.commit()
            return True
        except Exception as e:
            logger.error(f"Erro ao limpar notificacoes: {e}")
            return False

    def delete_old_notifications(self, days: int = 30) -> int:
        """Remove notificações antigas"""
        cutoff = (datetime.utcnow() - timedelta(days=days)).isoformat()
        
        cursor = self._conn.cursor()
        cursor.execute("""
            DELETE FROM notifications WHERE created_at < ?
        """, (cutoff,))
        
        deleted = cursor.rowcount
        self._conn.commit()
        return deleted


# Singleton
local_storage = LocalStorage()

"""
HelpState - Estado da Central de Ajuda
Gerencia busca, categorias e contato com envio real de email.
"""
import reflex as rx
from typing import List, Dict, Any
from .auth_state import AuthState


class HelpState(AuthState):
    """Estado responsável pela Central de Ajuda"""

    # Busca
    search_query: str = ""
    search_results: List[Dict[str, Any]] = []

    # Categoria selecionada
    selected_category: str = ""

    # Modal de contato
    show_contact_modal: bool = False
    contact_type: str = ""  # "chat", "email", "call"
    contact_name: str = ""
    contact_email: str = ""
    contact_subject: str = ""
    contact_message: str = ""
    is_sending_contact: bool = False
    contact_success: bool = False
    contact_error: str = ""

    # URLs de integração (configuráveis)
    calendly_url: str = "https://calendly.com/labbridge/suporte"
    intercom_app_id: str = ""  # Configurar quando tiver
    whatsapp_number: str = "5551991914837"  # Configurar com numero real em producao

    # Dados de categorias
    categories_data: List[Dict[str, Any]] = [
        {"id": "primeiros-passos", "title": "Primeiros Passos", "articles": 8, "icon": "rocket"},
        {"id": "auditorias", "title": "Auditorias", "articles": 12, "icon": "file-search"},
        {"id": "importacao", "title": "Importação de Dados", "articles": 6, "icon": "upload"},
        {"id": "relatorios", "title": "Relatórios", "articles": 9, "icon": "file-chart"},
        {"id": "integracoes", "title": "Integrações", "articles": 5, "icon": "plug"},
        {"id": "conta", "title": "Conta e Faturamento", "articles": 7, "icon": "credit-card"},
    ]

    # Dados de tutoriais
    tutorials_data: List[Dict[str, Any]] = [
        {"id": "primeira-auditoria", "title": "Criando sua primeira auditoria", "duration": "5 min", "url": "/help/tutorial/primeira-auditoria"},
        {"id": "importar-compulab", "title": "Importando dados do Compulab", "duration": "3 min", "url": "/help/tutorial/importar-compulab"},
        {"id": "analisar-divergencias", "title": "Analisando divergências", "duration": "8 min", "url": "/help/tutorial/analisar-divergencias"},
        {"id": "configurar-integracoes", "title": "Configurando integrações", "duration": "10 min", "url": "/help/tutorial/configurar-integracoes"},
    ]

    # FAQs
    faqs_data: List[Dict[str, Any]] = [
        {
            "q": "Como faço para criar minha primeira auditoria?",
            "a": "Acesse 'Auditorias' no menu lateral, clique em 'Nova Auditoria' e faça upload dos arquivos Compulab e SIMUS."
        },
        {
            "q": "Quais formatos de arquivo são aceitos?",
            "a": "Aceitamos arquivos .txt (Compulab), .xlsx, .xls e .csv para importação de dados."
        },
        {
            "q": "Como exportar relatórios em diferentes formatos?",
            "a": "Na página de Relatórios, selecione os dados e clique em Exportar. Você pode escolher PDF, Excel ou CSV."
        },
        {
            "q": "É possível adicionar mais usuários à minha conta?",
            "a": "Sim! Acesse 'Usuários & Permissões' no menu e convide novos membros com diferentes níveis de acesso."
        },
        {
            "q": "Como entrar em contato com o suporte técnico?",
            "a": "Use o formulário de contato abaixo, envie email para suporte@labbridge.com.br ou agende uma chamada."
        },
    ]

    def set_search_query(self, value: str):
        """Atualiza a busca"""
        self.search_query = value
        self._perform_search()

    def _perform_search(self):
        """Executa a busca nos artigos"""
        if not self.search_query.strip():
            self.search_results = []
            return

        query = self.search_query.lower()
        results = []

        # Busca em categorias
        for cat in self.categories_data:
            if query in cat["title"].lower():
                results.append({
                    "type": "category",
                    "title": cat["title"],
                    "id": cat["id"],
                    "icon": cat.get("icon", "folder")
                })

        # Busca em tutoriais
        for tut in self.tutorials_data:
            if query in tut["title"].lower():
                results.append({
                    "type": "tutorial",
                    "title": tut["title"],
                    "id": tut["id"],
                    "url": tut.get("url", "#")
                })

        # Busca em FAQs
        for faq in self.faqs_data:
            if query in faq["q"].lower() or query in faq["a"].lower():
                results.append({
                    "type": "faq",
                    "title": faq["q"],
                    "answer": faq["a"]
                })

        self.search_results = results[:10]

    def select_category(self, category_id: str):
        """Seleciona uma categoria"""
        self.selected_category = category_id
        return rx.toast.info(f"Categoria: {category_id} - Artigos em breve!")

    def open_tutorial(self, tutorial_id: str):
        """Abre um tutorial"""
        for tut in self.tutorials_data:
            if tut["id"] == tutorial_id:
                return rx.toast.info(f"Tutorial: {tut['title']} - Em desenvolvimento")
        return rx.toast.error("Tutorial não encontrado")

    def open_contact_modal(self, contact_type: str):
        """Abre o modal de contato"""
        self.contact_type = contact_type
        self.show_contact_modal = True
        self.contact_success = False
        self.contact_error = ""

    def close_contact_modal(self):
        """Fecha o modal de contato"""
        self.show_contact_modal = False
        self.contact_type = ""
        self.contact_name = ""
        self.contact_email = ""
        self.contact_subject = ""
        self.contact_message = ""
        self.contact_success = False
        self.contact_error = ""

    def set_contact_name(self, value: str):
        self.contact_name = value

    def set_contact_email(self, value: str):
        self.contact_email = value

    def set_contact_subject(self, value: str):
        self.contact_subject = value

    def set_contact_message(self, value: str):
        self.contact_message = value

    async def send_contact(self):
        """Envia mensagem de contato via email real"""
        self.is_sending_contact = True
        self.contact_error = ""
        yield

        try:
            # Validação
            if not self.contact_name.strip():
                self.contact_error = "Nome é obrigatório"
                self.is_sending_contact = False
                yield
                return

            if not self.contact_email.strip() or "@" not in self.contact_email:
                self.contact_error = "Email inválido"
                self.is_sending_contact = False
                yield
                return

            if not self.contact_message.strip():
                self.contact_error = "Mensagem é obrigatória"
                self.is_sending_contact = False
                yield
                return

            # Enviar email usando email_service
            from ..services.email_service import email_service
            
            subject = self.contact_subject if self.contact_subject.strip() else f"Contato de {self.contact_name}"
            
            html_content = f"""
            <div style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto;">
                <div style="background: linear-gradient(135deg, #1e6f9f 0%, #0ea5e9 100%); padding: 20px; text-align: center;">
                    <h1 style="color: white; margin: 0;">Nova Mensagem de Contato</h1>
                </div>
                <div style="padding: 20px; background: #f8fafc;">
                    <p><strong>Nome:</strong> {self.contact_name}</p>
                    <p><strong>Email:</strong> {self.contact_email}</p>
                    <p><strong>Tipo:</strong> {self.contact_type}</p>
                    <hr style="border: 1px solid #e2e8f0;">
                    <p><strong>Mensagem:</strong></p>
                    <div style="background: white; padding: 15px; border-radius: 8px; border: 1px solid #e2e8f0;">
                        {self.contact_message}
                    </div>
                </div>
                <div style="background: #f1f5f9; padding: 15px; text-align: center; font-size: 12px; color: #64748b;">
                    Enviado via Central de Ajuda LabBridge
                </div>
            </div>
            """

            # Enviar para suporte
            success, error = await email_service.send_email(
                to_email="suporte@labbridge.com.br",  # Email de suporte
                subject=f"[Suporte LabBridge] {subject}",
                html_content=html_content
            )

            if success:
                self.contact_success = True
                self.is_sending_contact = False
                
                # Registrar atividade
                from ..services.local_storage import local_storage
                local_storage.add_activity_log(
                    tenant_id=self.current_user.tenant_id if self.current_user else "",
                    action="Contato enviado",
                    details=f"Email de suporte enviado: {subject}",
                    user=self.contact_name
                )
                
                # Criar notificação
                from ..states.notification_state import NotificationState
                NotificationState.create_notification(
                    title="Mensagem Enviada",
                    message="Sua mensagem foi enviada para o suporte. Responderemos em breve!",
                    type="success"
                )
                
                yield
                
                # Fecha modal após 2 segundos
                import asyncio
                await asyncio.sleep(2)
                self.close_contact_modal()
            else:
                # Email falhou - informar o usuario
                self.contact_error = "Nao foi possivel enviar a mensagem. Tente novamente mais tarde."
                self.contact_success = False
                self.is_sending_contact = False

        except Exception as e:
            self.contact_error = f"Erro ao enviar: {str(e)}"
            self.is_sending_contact = False

        yield

    def start_chat(self):
        """Inicia chat ao vivo (Intercom ou WhatsApp)"""
        if self.whatsapp_number:
            return rx.redirect(f"https://wa.me/{self.whatsapp_number}?text=Olá! Preciso de ajuda com o LabBridge.")
        return rx.toast.info("Chat ao vivo - Em desenvolvimento. Use o formulário de contato.")

    def open_whatsapp(self):
        """Abre WhatsApp com mensagem pré-definida"""
        message = "Olá! Preciso de ajuda com o LabBridge."
        return rx.redirect(f"https://wa.me/{self.whatsapp_number}?text={message}")

    def send_email_direct(self):
        """Abre cliente de email"""
        return rx.redirect("mailto:suporte@labbridge.com.br?subject=Suporte LabBridge")

    def schedule_call(self):
        """Agendar chamada via Calendly"""
        if self.calendly_url:
            return rx.redirect(self.calendly_url)
        return rx.toast.info("Agendamento de chamada - Configure o link do Calendly nas configurações.")

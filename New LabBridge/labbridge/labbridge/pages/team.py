"""
LabBridge - Usuários & Permissões
Página funcional com CRUD completo de membros
"""
import reflex as rx
from ..states.team_state import TeamState
from ..styles import Color, Design, Spacing, TextSize
from ..components import ui


def role_badge(role: str) -> rx.Component:
    """Badge de função do usuário"""
    role_config = {
        "admin_global": (Color.ERROR, Color.ERROR_BG, "shield"),
        "admin_lab": (Color.PRIMARY, Color.PRIMARY_LIGHT, "shield-check"),
        "analyst": (Color.SUCCESS, Color.SUCCESS_BG, "user-check"),
        "viewer": (Color.TEXT_SECONDARY, Color.BACKGROUND, "eye"),
    }
    color, bg, icon = role_config.get(role, role_config["viewer"])

    role_names = {
        "admin_global": "Admin Global",
        "admin_lab": "Admin Lab",
        "analyst": "Analista",
        "viewer": "Visualizador"
    }
    display_name = role_names.get(role, "Visualizador")

    return rx.hstack(
        rx.icon(tag=icon, size=12, color=color),
        rx.text(display_name, font_size=TextSize.CAPTION, font_weight="500", color=color),
        spacing="1",
        padding_x="8px",
        padding_y="4px",
        bg=bg,
        border_radius="full",
    )


def user_row(member: dict) -> rx.Component:
    """Linha de usuário na tabela"""
    name = member["name"]
    email = member["email"]
    role = member["role"]
    status = member["status"]
    member_id = member["id"]
    last_active = member["last_active"]

    return rx.hstack(
        # User Info
        rx.hstack(
            rx.avatar(
                fallback=name,
                size="2",
                radius="full",
                bg=rx.cond(status == "active", Color.PRIMARY, Color.TEXT_MUTED),
                color="white",
            ),
            rx.vstack(
                rx.text(name, font_weight="500", color=Color.TEXT_PRIMARY),
                rx.text(email, font_size=TextSize.CAPTION, color=Color.TEXT_SECONDARY),
                spacing="0",
                align_items="start",
            ),
            spacing="3",
            align="center",
            min_width="200px",
        ),

        # Role
        rx.box(
            role_badge(role),
            min_width="120px",
        ),

        # Status
        rx.box(
            rx.hstack(
                rx.box(
                    width="8px",
                    height="8px",
                    bg=rx.cond(
                        status == "active",
                        Color.SUCCESS,
                        rx.cond(status == "pending", Color.WARNING, Color.TEXT_MUTED)
                    ),
                    border_radius="full",
                ),
                rx.text(
                    rx.cond(
                        status == "active",
                        "Ativo",
                        rx.cond(status == "pending", "Pendente", "Inativo")
                    ),
                    font_size=TextSize.SMALL,
                    color=rx.cond(
                        status == "active",
                        Color.SUCCESS,
                        rx.cond(status == "pending", Color.WARNING_HOVER, Color.TEXT_SECONDARY)
                    ),
                ),
                spacing="2",
                align="center",
            ),
            min_width="100px",
        ),

        # Last Active
        rx.box(
            rx.cond(
                last_active != "",
                rx.text(last_active, font_size=TextSize.SMALL, color=Color.TEXT_SECONDARY),
                rx.text("-", font_size=TextSize.SMALL, color=Color.TEXT_SECONDARY),
            ),
            min_width="100px",
            display=["none", "none", "block"],
        ),

        rx.spacer(),

        # Actions
        rx.hstack(
            rx.menu.root(
                rx.menu.trigger(
                    rx.button(
                        rx.icon(tag="ellipsis-vertical", size=16),
                        variant="ghost",
                        size="1",
                        cursor="pointer",
                    ),
                ),
                rx.menu.content(
                    rx.menu.item(
                        rx.hstack(rx.icon(tag="pencil", size=14), rx.text("Editar")),
                        on_select=lambda: TeamState.open_edit_modal(member_id),
                    ),
                    rx.menu.item(
                        rx.hstack(rx.icon(tag="key", size=14), rx.text("Alterar Permissões")),
                        on_select=lambda: TeamState.open_edit_modal(member_id),
                    ),
                    rx.menu.separator(),
                    rx.cond(
                        status == "pending",
                        rx.menu.item(
                            rx.hstack(rx.icon(tag="mail", size=14), rx.text("Reenviar Convite")),
                            on_select=lambda: TeamState.resend_member_invite(member_id),
                        ),
                        rx.fragment(),
                    ),
                    rx.cond(
                        status == "active",
                        rx.menu.item(
                            rx.hstack(rx.icon(tag="user-x", size=14), rx.text("Desativar")),
                            color="red",
                            on_select=lambda: TeamState.toggle_member_status(member_id),
                        ),
                        rx.cond(
                            status == "inactive",
                            rx.menu.item(
                                rx.hstack(rx.icon(tag="user-check", size=14), rx.text("Ativar")),
                                color="green",
                                on_select=lambda: TeamState.toggle_member_status(member_id),
                            ),
                            rx.fragment(),
                        ),
                    ),
                    rx.menu.separator(),
                    rx.menu.item(
                        rx.hstack(rx.icon(tag="trash-2", size=14), rx.text("Remover")),
                        color="red",
                        on_select=lambda: TeamState.remove_member(member_id),
                    ),
                ),
            ),
            spacing="1",
        ),

        width="100%",
        padding=Spacing.MD,
        border_bottom=f"1px solid {Color.BORDER}",
        transition="all 0.15s ease",
        _hover={"bg": Color.PRIMARY_LIGHT},
    )


def role_permission_card(role: str, description: str, permissions: list) -> rx.Component:
    """Card de explicação de papel"""
    role_config = {
        "admin_global": (Color.ERROR, "shield"),
        "admin_lab": (Color.PRIMARY, "shield-check"),
        "analyst": (Color.SUCCESS, "user-check"),
        "viewer": (Color.TEXT_SECONDARY, "eye"),
    }
    color, icon = role_config.get(role, role_config["viewer"])

    role_names = {
        "admin_global": "Admin Global",
        "admin_lab": "Admin Lab",
        "analyst": "Analista",
        "viewer": "Visualizador"
    }
    display_name = role_names.get(role, role)

    return rx.box(
        rx.vstack(
            rx.hstack(
                rx.box(
                    rx.icon(tag=icon, size=20, color=color),
                    padding="8px",
                    bg=f"{color}15",
                    border_radius=Design.RADIUS_MD,
                ),
                rx.vstack(
                    rx.text(display_name, font_weight="600", color=Color.TEXT_PRIMARY),
                    rx.text(description, font_size="0.75rem", color=Color.TEXT_SECONDARY),
                    spacing="0",
                    align_items="start",
                ),
                spacing="3",
                width="100%",
            ),
            rx.vstack(
                *[
                    rx.hstack(
                        rx.icon(tag="check", size=14, color=Color.SUCCESS),
                        rx.text(perm, font_size="0.75rem", color=Color.TEXT_SECONDARY),
                        spacing="2",
                    )
                    for perm in permissions
                ],
                spacing="1",
                align_items="start",
                margin_top=Spacing.SM,
            ),
            width="100%",
            spacing="0",
        ),
        bg=Color.SURFACE,
        border=f"1px solid {Color.BORDER}",
        border_radius=Design.RADIUS_LG,
        padding=Spacing.MD,
    )


def invite_modal() -> rx.Component:
    """Modal de convite de usuário"""
    return rx.dialog.root(
        rx.dialog.trigger(
            ui.button("Convidar Membro", icon="user-plus", on_click=TeamState.open_invite_modal),
        ),
        rx.dialog.content(
            rx.dialog.title("Convidar Novo Membro"),
            rx.dialog.description(
                "Envie um convite por e-mail para adicionar um novo membro à equipe.",
                margin_bottom=Spacing.LG,
            ),
            rx.vstack(
                rx.vstack(
                    rx.text("E-mail", font_weight="500", font_size=TextSize.SMALL),
                    ui.input(
                        placeholder="email@exemplo.com",
                        type="email",
                        width="100%",
                        value=TeamState.invite_email,
                        on_change=TeamState.set_invite_email,
                    ),
                    spacing="1",
                    width="100%",
                ),
                rx.vstack(
                    rx.text("Função", font_weight="500", font_size=TextSize.SMALL),
                    rx.select(
                        ["viewer", "analyst", "admin_lab", "admin_global"],
                        default_value="viewer",
                        value=TeamState.invite_role,
                        on_change=TeamState.set_invite_role,
                        width="100%",
                    ),
                    spacing="1",
                    width="100%",
                ),
                rx.vstack(
                    rx.text("Mensagem (opcional)", font_weight="500", font_size=TextSize.SMALL),
                    rx.text_area(
                        placeholder="Adicione uma mensagem personalizada ao convite...",
                        width="100%",
                        min_height="80px",
                        value=TeamState.invite_message,
                        on_change=TeamState.set_invite_message,
                    ),
                    spacing="1",
                    width="100%",
                ),
                # Error message
                rx.cond(
                    TeamState.error_message != "",
                    rx.box(
                        rx.hstack(
                            rx.icon(tag="circle-alert", size=16, color=Color.ERROR),
                            rx.text(TeamState.error_message, color=Color.ERROR, font_size="0.875rem"),
                            spacing="2",
                        ),
                        bg=Color.ERROR_BG,
                        padding="12px",
                        border_radius="8px",
                        width="100%",
                    ),
                ),
                spacing="4",
                width="100%",
            ),
            rx.hstack(
                rx.dialog.close(
                    ui.button("Cancelar", variant="ghost", on_click=TeamState.close_invite_modal),
                ),
                rx.cond(
                    TeamState.is_saving,
                    rx.button(
                        rx.spinner(size="1"),
                        "Enviando...",
                        disabled=True,
                    ),
                    rx.dialog.close(
                        ui.button(
                            "Enviar Convite",
                            variant="primary",
                            icon="send",
                            on_click=TeamState.send_invite,
                        ),
                    ),
                ),
                spacing="2",
                justify="end",
                margin_top=Spacing.LG,
            ),
            max_width="450px",
        ),
        open=TeamState.show_invite_modal,
    )


def edit_modal() -> rx.Component:
    """Modal de edição de membro"""
    return rx.dialog.root(
        rx.dialog.content(
            rx.dialog.title("Editar Membro"),
            rx.vstack(
                rx.vstack(
                    rx.text("Nome", font_weight="500", font_size=TextSize.SMALL),
                    ui.input(
                        placeholder="Nome do membro",
                        width="100%",
                        value=TeamState.edit_member_name,
                        on_change=TeamState.set_edit_name,
                    ),
                    spacing="1",
                    width="100%",
                ),
                rx.vstack(
                    rx.text("Função", font_weight="500", font_size=TextSize.SMALL),
                    rx.select(
                        ["viewer", "analyst", "admin_lab", "admin_global"],
                        value=TeamState.edit_member_role,
                        on_change=TeamState.set_edit_role,
                        width="100%",
                    ),
                    spacing="1",
                    width="100%",
                ),
                rx.cond(
                    TeamState.error_message != "",
                    rx.box(
                        rx.text(TeamState.error_message, color=Color.ERROR, font_size="0.875rem"),
                        bg=Color.ERROR_BG,
                        padding="12px",
                        border_radius="8px",
                        width="100%",
                    ),
                ),
                spacing="4",
                width="100%",
            ),
            rx.hstack(
                ui.button("Cancelar", variant="ghost", on_click=TeamState.close_edit_modal),
                ui.button(
                    "Salvar",
                    variant="primary",
                    on_click=TeamState.save_member_edit,
                    disabled=TeamState.is_saving,
                ),
                spacing="2",
                justify="end",
                margin_top=Spacing.LG,
            ),
            max_width="400px",
        ),
        open=TeamState.show_edit_modal,
    )


def team_page() -> rx.Component:
    """Página de Gestão de Usuários"""
    return rx.box(
        rx.vstack(
            # Page Header
            ui.page_header(
                title="Usuários & Permissões",
                description="Gerencie sua equipe e controle de acesso",
                actions=invite_modal(),
            ),

            # Success Message Toast
            rx.cond(
                TeamState.success_message != "",
                rx.box(
                    rx.hstack(
                        rx.icon(tag="circle-check", size=20, color=Color.SUCCESS),
                        rx.text(TeamState.success_message, color=Color.SUCCESS),
                        rx.spacer(),
                        rx.button(
                            rx.icon(tag="x", size=14),
                            variant="ghost",
                            size="1",
                            on_click=TeamState.clear_messages,
                        ),
                        spacing="2",
                        width="100%",
                    ),
                    bg=Color.SUCCESS_BG,
                    border=f"1px solid {Color.SUCCESS}40",
                    padding=Spacing.MD,
                    border_radius=Design.RADIUS_LG,
                    margin_bottom=Spacing.MD,
                ),
            ),

            # Stats
            rx.grid(
                rx.box(
                    rx.hstack(
                        rx.box(
                            rx.icon(tag="users", size=20, color=Color.PRIMARY),
                            padding="10px",
                            bg=Color.PRIMARY_LIGHT,
                            border_radius=Design.RADIUS_MD,
                        ),
                        rx.vstack(
                            rx.text(TeamState.total_members, font_size="1.5rem", font_weight="700", color=Color.DEEP),
                            rx.text("Total de Usuários", font_size="0.75rem", color=Color.TEXT_SECONDARY),
                            spacing="0",
                            align_items="start",
                        ),
                        spacing="3",
                    ),
                    bg=Color.SURFACE,
                    border=f"1px solid {Color.BORDER}",
                    border_radius=Design.RADIUS_LG,
                    padding=Spacing.MD,
                ),
                rx.box(
                    rx.hstack(
                        rx.box(
                            rx.icon(tag="user-check", size=20, color=Color.SUCCESS),
                            padding="10px",
                            bg=Color.SUCCESS_BG,
                            border_radius=Design.RADIUS_MD,
                        ),
                        rx.vstack(
                            rx.text(TeamState.active_members_count, font_size="1.5rem", font_weight="700", color=Color.SUCCESS),
                            rx.text("Ativos", font_size="0.75rem", color=Color.TEXT_SECONDARY),
                            spacing="0",
                            align_items="start",
                        ),
                        spacing="3",
                    ),
                    bg=Color.SURFACE,
                    border=f"1px solid {Color.BORDER}",
                    border_radius=Design.RADIUS_LG,
                    padding=Spacing.MD,
                ),
                rx.box(
                    rx.hstack(
                        rx.box(
                            rx.icon(tag="clock", size=20, color=Color.WARNING),
                            padding="10px",
                            bg=Color.WARNING_BG,
                            border_radius=Design.RADIUS_MD,
                        ),
                        rx.vstack(
                            rx.text(TeamState.pending_members_count, font_size="1.5rem", font_weight="700", color=Color.WARNING_HOVER),
                            rx.text("Pendentes", font_size="0.75rem", color=Color.TEXT_SECONDARY),
                            spacing="0",
                            align_items="start",
                        ),
                        spacing="3",
                    ),
                    bg=Color.SURFACE,
                    border=f"1px solid {Color.BORDER}",
                    border_radius=Design.RADIUS_LG,
                    padding=Spacing.MD,
                ),
                rx.box(
                    rx.hstack(
                        rx.box(
                            rx.icon(tag="shield", size=20, color=Color.ERROR),
                            padding="10px",
                            bg=Color.ERROR_BG,
                            border_radius=Design.RADIUS_MD,
                        ),
                        rx.vstack(
                            rx.text(TeamState.admin_count, font_size="1.5rem", font_weight="700", color=Color.ERROR),
                            rx.text("Admins", font_size="0.75rem", color=Color.TEXT_SECONDARY),
                            spacing="0",
                            align_items="start",
                        ),
                        spacing="3",
                    ),
                    bg=Color.SURFACE,
                    border=f"1px solid {Color.BORDER}",
                    border_radius=Design.RADIUS_LG,
                    padding=Spacing.MD,
                ),
                columns=rx.breakpoints(initial="2", md="4"),
                spacing="4",
                width="100%",
                margin_bottom=Spacing.LG,
            ),

            # Main Content Grid
            rx.grid(
                # Users List
                rx.box(
                    rx.vstack(
                        rx.hstack(
                            rx.text("Membros da Equipe", font_weight="600", color=Color.TEXT_PRIMARY),
                            rx.spacer(),
                            ui.input(
                                placeholder="Buscar usuário...",
                                width="200px",
                                value=TeamState.search_query,
                                on_change=TeamState.set_search_query,
                            ),
                            width="100%",
                            align="center",
                            margin_bottom=Spacing.MD,
                        ),
                        # Table Header
                        rx.hstack(
                            rx.text("Usuário", font_size="0.75rem", font_weight="600", color=Color.TEXT_SECONDARY, min_width="200px"),
                            rx.text("Função", font_size="0.75rem", font_weight="600", color=Color.TEXT_SECONDARY, min_width="120px"),
                            rx.text("Status", font_size="0.75rem", font_weight="600", color=Color.TEXT_SECONDARY, min_width="100px"),
                            rx.text("Última Atividade", font_size="0.75rem", font_weight="600", color=Color.TEXT_SECONDARY, min_width="100px", display=["none", "none", "block"]),
                            rx.spacer(),
                            rx.text("Ações", font_size="0.75rem", font_weight="600", color=Color.TEXT_SECONDARY),
                            width="100%",
                            padding_x=Spacing.MD,
                            padding_bottom=Spacing.SM,
                            border_bottom=f"2px solid {Color.BORDER}",
                        ),
                        # User Rows - Dynamic
                        rx.cond(
                            TeamState.is_loading,
                            rx.center(
                                rx.vstack(
                                    rx.spinner(size="3", color=Color.PRIMARY),
                                    rx.text("Carregando equipe...", color=Color.TEXT_SECONDARY),
                                    spacing="3",
                                ),
                                padding=Spacing.XXL,
                            ),
                            rx.foreach(
                                TeamState.filtered_members,
                                user_row,
                            ),
                        ),
                        width="100%",
                        spacing="0",
                    ),
                    bg=Color.SURFACE,
                    border=f"1px solid {Color.BORDER}",
                    border_radius=Design.RADIUS_XL,
                    padding=Spacing.LG,
                    overflow_x="auto",
                ),

                # Roles Explanation
                rx.vstack(
                    rx.text("Níveis de Acesso", font_weight="600", color=Color.TEXT_PRIMARY, margin_bottom=Spacing.MD),
                    role_permission_card(
                        "admin_global",
                        "Controle total do sistema",
                        ["Gerenciar usuários", "Configurações globais", "Acesso a todos os dados", "Faturamento"],
                    ),
                    role_permission_card(
                        "admin_lab",
                        "Gerência do laboratório",
                        ["Gerenciar usuários do lab", "Criar auditorias", "Exportar relatórios"],
                    ),
                    role_permission_card(
                        "analyst",
                        "Operações do dia a dia",
                        ["Criar auditorias", "Editar dados", "Gerar relatórios"],
                    ),
                    role_permission_card(
                        "viewer",
                        "Apenas leitura",
                        ["Visualizar auditorias", "Visualizar relatórios"],
                    ),
                    spacing="3",
                    width="100%",
                ),

                columns=rx.breakpoints(initial="1", lg="2"),
                spacing="4",
                width="100%",
            ),

            # Edit Modal
            edit_modal(),

            width="100%",
            spacing="0",
        ),
        width="100%",
        on_mount=TeamState.load_team_members,
    )

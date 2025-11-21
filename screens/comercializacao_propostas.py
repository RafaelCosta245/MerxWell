from typing import Any, Dict, Optional, List
from datetime import datetime

import flet as ft
from scripts.database import read_records

def _format_date(value: Any) -> str:
    """Formata datas ISO/DateTime como dd/mm/aaaa."""
    if value is None:
        return "-"
    s = str(value)
    if not s:
        return "-"
    try:
        # Tenta parse ISO completo
        dt = datetime.fromisoformat(s.replace("Z", "+00:00"))
        return dt.strftime("%d/%m/%Y")
    except Exception:
        # Fallback em caso de formato inesperado
        if len(s) >= 10:
            return f"{s[8:10]}/{s[5:7]}/{s[0:4]}"
        return s


def _create_proposals_table(
    proposals: list[Dict[str, Any]],
    screen: Any,
) -> ft.Control:
    headers = [
        "Comprador",
        "Vendedor",
        "Data",
        "Status",
        "Editar",
        "Gerar",
        "Excluir",
        "Contrato",
    ]

    widths = [250, 200, 120, 80, 70, 70, 70, 80]

    def header_cell(text: str, width: int) -> ft.Control:
        return ft.Container(
            content=ft.Text(
                text,
                size=13,
                weight=ft.FontWeight.BOLD,
                color=ft.Colors.WHITE,
                text_align=ft.TextAlign.CENTER,
            ),
            width=width,
            height=44,
            bgcolor=ft.Colors.BLUE_700,
            padding=10,
            alignment=ft.alignment.center,
            border=ft.border.all(1, ft.Colors.BLUE_900),
        )

    def data_cell(content: ft.Control, width: int, row_index: int) -> ft.Control:
        bg_color = ft.Colors.WHITE if row_index % 2 == 0 else ft.Colors.GREY_50
        return ft.Container(
            content=content,
            width=width,
            height=40,
            bgcolor=bg_color,
            padding=10,
            alignment=ft.alignment.center,
            border=ft.border.all(1, ft.Colors.GREY_300),
        )

    def action_button(
        icon: str,
        tooltip: str,
        width: int,
        row_index: int,
        on_click,
        icon_color: str = ft.Colors.BLACK,
    ) -> ft.Control:
        bg_color = ft.Colors.WHITE if row_index % 2 == 0 else ft.Colors.GREY_50
        return ft.Container(
            content=ft.IconButton(
                icon=icon,
                icon_color=icon_color,
                tooltip=tooltip,
                on_click=on_click,
                icon_size=20,
            ),
            width=width,
            height=40,
            bgcolor=bg_color,
            alignment=ft.alignment.center,
            border=ft.border.all(1, ft.Colors.GREY_300),
        )

    header_row = ft.Row(
        controls=[header_cell(headers[i], widths[i]) for i in range(len(headers))],
        spacing=0,
    )

    data_rows: list[ft.Control] = []
    for idx, p in enumerate(proposals):
        buyer = str(p.get("customer_name") or "-")
        seller = "-" # Placeholder as per instructions (DB doesn't have seller column yet)
        date_str = _format_date(p.get("created_at"))
        status_val = str(p.get("status") or "PENDING")

        # Status Icon Logic
        if status_val == "ACCEPTED":
            status_icon = ft.Icon(ft.Icons.CHECK_CIRCLE, color=ft.Colors.GREEN, size=20, tooltip="Aceita")
        else:
            status_icon = ft.Icon(ft.Icons.HOURGLASS_EMPTY, color=ft.Colors.ORANGE, size=20, tooltip="Pendente")

        def make_edit_action(proposal_data):
            def handler(_):
                print(f"DEBUG: Edit clicked for proposal {proposal_data.get('id')}")
                # Future implementation: Navigate to edit screen
            return handler

        def make_generate_action(proposal_data):
            def handler(_):
                print(f"DEBUG: Generate proposal clicked for {proposal_data.get('id')}")
                # Future implementation: Generate PDF/Doc
            return handler

        def make_delete_action(proposal_data):
            def handler(_):
                print(f"DEBUG: Delete clicked for proposal {proposal_data.get('id')}")
                # Future implementation: Delete logic
            return handler
            
        def make_contract_action(proposal_data):
            def handler(_):
                print(f"DEBUG: Generate Contract clicked for proposal {proposal_data.get('id')}")
                # Future implementation: Generate Contract PDF
            return handler

        row = ft.Row(
            controls=[
                data_cell(ft.Text(buyer, size=12, color=ft.Colors.GREY_900, text_align=ft.TextAlign.CENTER), widths[0], idx),
                data_cell(ft.Text(seller, size=12, color=ft.Colors.GREY_900, text_align=ft.TextAlign.CENTER), widths[1], idx),
                data_cell(ft.Text(date_str, size=12, color=ft.Colors.GREY_900, text_align=ft.TextAlign.CENTER), widths[2], idx),
                data_cell(status_icon, widths[3], idx),
                action_button(ft.Icons.EDIT, "Editar proposta", widths[4], idx, make_edit_action(p)),
                action_button(ft.Icons.DESCRIPTION, "Gerar proposta", widths[5], idx, make_generate_action(p)),
                action_button(ft.Icons.DELETE, "Excluir proposta", widths[6], idx, make_delete_action(p)),
                action_button(ft.Icons.PICTURE_AS_PDF, "Gerar Contrato", widths[7], idx, make_contract_action(p), icon_color=ft.Colors.RED_700),
            ],
            spacing=0,
        )
        data_rows.append(row)

    total_width = sum(widths)

    table_column = ft.Column(
        controls=[header_row] + data_rows,
        spacing=0,
        scroll=ft.ScrollMode.AUTO,
    )

    return ft.Container(
        content=table_column,
        width=total_width,
        border=ft.border.all(1, ft.Colors.GREY_300),
        border_radius=8,
        bgcolor=ft.Colors.WHITE,
    )


def create_propostas_content(screen: Any) -> ft.Control:
    """Conteúdo da aba Propostas com tabela em container e scroll."""
    
    # Container para a tabela que será atualizado
    table_container = ft.Container()

    def load_proposals(search_term: str = ""):
        print(f"DEBUG: Loading proposals with search_term='{search_term}'")
        try:
            # Fetch all proposals (filtering in memory for partial match)
            all_proposals = read_records("proposals")
            
            if search_term:
                filtered_proposals = [
                    p for p in all_proposals 
                    if search_term.lower() in str(p.get("customer_name", "")).lower()
                ]
            else:
                filtered_proposals = all_proposals
            
            # Sort by created_at desc (optional, but good for UX)
            filtered_proposals.sort(key=lambda x: x.get("created_at", ""), reverse=True)

            table_container.content = _create_proposals_table(filtered_proposals, screen)
            table_container.update()
            
        except Exception as e:
            print(f"ERROR: Failed to load proposals: {e}")
            table_container.content = ft.Text(f"Erro ao carregar propostas: {e}", color=ft.Colors.RED)
            table_container.update()

    buyer_field = ft.TextField(
        label="Comprador",
        prefix_icon=ft.Icons.SEARCH,
        width=260,
        on_submit=lambda e: load_proposals(e.control.value)
    )

    seller_field = ft.TextField(
        label="Vendedor",
        prefix_icon=ft.Icons.SEARCH,
        width=260,
        visible=False # Hidden as requested
    )

    def apply_filters(_: ft.ControlEvent) -> None:
        load_proposals(buyer_field.value)

    filters_row = ft.Row(
        controls=[buyer_field, seller_field],
        spacing=16,
        alignment=ft.MainAxisAlignment.START,
    )

    button_width = 170
    button_height = 40

    search_button = ft.ElevatedButton(
        text="Pesquisar",
        icon=ft.Icons.SEARCH,
        bgcolor=ft.Colors.BLUE_600,
        color=ft.Colors.WHITE,
        style=ft.ButtonStyle(
            shape=ft.RoundedRectangleBorder(radius=6),
            padding=ft.padding.symmetric(horizontal=0, vertical=0),
        ),
        width=button_width,
        height=button_height,
        on_click=apply_filters,
    )

    new_proposal_button = ft.ElevatedButton(
        text="Nova Proposta",
        icon=ft.Icons.ADD,
        bgcolor=ft.Colors.BLUE_600,
        color=ft.Colors.WHITE,
        style=ft.ButtonStyle(
            shape=ft.RoundedRectangleBorder(radius=6),
            padding=ft.padding.symmetric(horizontal=0, vertical=0),
        ),
        width=button_width,
        height=button_height,
        on_click=lambda _: screen.navigation.go(
            "/comercializacao",
            params={
                "submenu": "propostas",
                "propostas_view": "new",
            },
        ),
    )

    actions_row = ft.Row(
        controls=[
            search_button,
            new_proposal_button,
        ],
        spacing=12,
        alignment=ft.MainAxisAlignment.START,
    )

    # Initial Load
    # We need to use a threading timer or similar if we want to load immediately without blocking, 
    # but since this is called during build, we can just call it or let the user search.
    # Better to load initially.
    # However, calling update() inside build() might be tricky if not added to page yet.
    # We can return the container with initial data if we fetch synchronously here, 
    # or use `did_mount` if we were in a Control class. 
    # Since this is a function returning controls, we can just fetch and build.
    
    try:
        initial_proposals = read_records("proposals")
        initial_proposals.sort(key=lambda x: x.get("created_at", ""), reverse=True)
        table_container.content = _create_proposals_table(initial_proposals, screen)
    except Exception as e:
        table_container.content = ft.Text(f"Erro ao carregar propostas: {e}", color=ft.Colors.RED)

    return ft.Container(
        expand=True,
        padding=20,
        content=ft.Column(
            controls=[
                ft.Text("Gerenciamento de Propostas", size=24, weight=ft.FontWeight.BOLD),
                ft.Container(height=10),
                filters_row,
                ft.Container(height=12),
                actions_row,
                ft.Container(height=16),
                ft.Row(
                    controls=[table_container],
                    scroll=ft.ScrollMode.ALWAYS,
                ),
            ],
            spacing=6,
            alignment=ft.MainAxisAlignment.START,
        ),
    )

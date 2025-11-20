from typing import Any, Dict, Optional
from datetime import datetime

import flet as ft

# Mock data for proposals - eventually this will come from the database
MOCK_PROPOSALS = [
    {
        "id": "1",
        "buyer": "Empresa A",
        "seller": "Empresa B",
        "date": "2023-10-27",
        "status": "Em Aberto",
    },
    {
        "id": "2",
        "buyer": "Indústria X",
        "seller": "Comercializadora Y",
        "date": "2023-11-15",
        "status": "Fechado",
    },
    {
        "id": "3",
        "buyer": "Cliente Z",
        "seller": "Fornecedor W",
        "date": "2023-12-01",
        "status": "Cancelado",
    },
]

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
        "ID",
        "Comprador",
        "Vendedor",
        "Data",
        "Status",
        "Editar",
        "Gerar",
        "Excluir",
    ]

    widths = [60, 250, 250, 120, 120, 80, 80, 80]

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

    def data_cell(text: str, width: int, row_index: int) -> ft.Control:
        bg_color = ft.Colors.WHITE if row_index % 2 == 0 else ft.Colors.GREY_50
        return ft.Container(
            content=ft.Text(
                text,
                size=12,
                color=ft.Colors.GREY_900,
                text_align=ft.TextAlign.CENTER,
            ),
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
    ) -> ft.Control:
        bg_color = ft.Colors.WHITE if row_index % 2 == 0 else ft.Colors.GREY_50
        return ft.Container(
            content=ft.IconButton(
                icon=icon,
                icon_color=ft.Colors.BLACK,
                tooltip=tooltip,
                on_click=on_click,
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
        p_id = str(p.get("id") or "-")
        buyer = str(p.get("buyer") or "-")
        seller = str(p.get("seller") or "-")
        date_str = _format_date(p.get("date"))
        status = str(p.get("status") or "-")

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

        row = ft.Row(
            controls=[
                data_cell(p_id, widths[0], idx),
                data_cell(buyer, widths[1], idx),
                data_cell(seller, widths[2], idx),
                data_cell(date_str, widths[3], idx),
                data_cell(status, widths[4], idx),
                action_button(
                    ft.Icons.EDIT,
                    "Editar proposta",
                    widths[5],
                    idx,
                    make_edit_action(p),
                ),
                action_button(
                    ft.Icons.DESCRIPTION,
                    "Gerar proposta",
                    widths[6],
                    idx,
                    make_generate_action(p),
                ),
                action_button(
                    ft.Icons.DELETE,
                    "Excluir proposta",
                    widths[7],
                    idx,
                    make_delete_action(p),
                ),
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
    
    # Mock filtering logic
    buyer_field = ft.TextField(
        label="Comprador",
        prefix_icon=ft.Icons.SEARCH,
        width=260,
    )

    seller_field = ft.TextField(
        label="Vendedor",
        prefix_icon=ft.Icons.SEARCH,
        width=260,
    )

    def apply_filters(_: ft.ControlEvent) -> None:
        print(f"DEBUG: Filtering proposals by Buyer={buyer_field.value}, Seller={seller_field.value}")
        # Future implementation: Filter MOCK_PROPOSALS or fetch from DB

    # Enter nos campos dispara a mesma ação do botão Pesquisar
    buyer_field.on_submit = apply_filters
    seller_field.on_submit = apply_filters

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

    table = _create_proposals_table(MOCK_PROPOSALS, screen)

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
                    controls=[table],
                    scroll=ft.ScrollMode.ALWAYS,
                ),
            ],
            spacing=6,
            alignment=ft.MainAxisAlignment.START,
        ),
    )

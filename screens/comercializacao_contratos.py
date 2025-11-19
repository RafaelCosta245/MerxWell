from typing import Any, Dict, Optional
from datetime import datetime

import flet as ft

from scripts.comercializacao_service import list_contracts_for_table


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


def _create_contracts_table(
    contracts: list[Dict[str, Any]],
    screen: Any,
    buyer_value: str,
    seller_value: str,
) -> ft.Control:
    headers = [
        "Cód. Contrato",
        "Comprador",
        "Vendedor",
        "Energia",
        "Início",
        "Fim",
        "Editar",
        "Sazo",
        "Excluir",
    ]

    widths = [130, 220, 220, 110, 110, 110, 80, 80, 80]

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
    for idx, c in enumerate(contracts):
        code = str(c.get("contract_code") or "-")
        contractor = str(c.get("contractor") or "-")
        seller = str(c.get("service_provider") or "-")
        energy = str(c.get("energy_source_type") or "-")
        start = _format_date(c.get("contract_start_date"))
        end = _format_date(c.get("contract_end_date"))

        def make_on_click(action: str, contract_code: str):
            return lambda _: print(f"Ação {action} para contrato {contract_code}")

        def make_sazo_action(contract_data):
            return lambda _: screen.navigation.go(
                "/comercializacao",
                params={
                    "submenu": "contratos",
                    "contracts_view": "sazo",
                    "contract_id": str(contract_data.get("id") or ""),
                    "start_date": str(contract_data.get("contract_start_date") or ""),
                    "end_date": str(contract_data.get("contract_end_date") or ""),
                    "buyer": buyer_value,
                    "seller": seller_value,
                },
            )

        def make_edit_action(contract_data):
            return lambda _: screen.navigation.go(
                "/comercializacao",
                params={
                    "submenu": "contratos",
                    "contracts_view": "new",
                    "contract_id": str(contract_data.get("id") or ""),
                    "buyer": buyer_value,
                    "seller": seller_value,
                },
            )

        row = ft.Row(
            controls=[
                data_cell(code, widths[0], idx),
                data_cell(contractor, widths[1], idx),
                data_cell(seller, widths[2], idx),
                data_cell(energy, widths[3], idx),
                data_cell(start, widths[4], idx),
                data_cell(end, widths[5], idx),
                action_button(
                    ft.Icons.EDIT,
                    "Editar contrato",
                    widths[6],
                    idx,
                    make_edit_action(c),
                ),
                action_button(
                    ft.Icons.CALENDAR_MONTH,
                    "Editar sazonalidade",
                    widths[7],
                    idx,
                    make_sazo_action(c),
                ),
                action_button(
                    ft.Icons.DELETE,
                    "Excluir contrato",
                    widths[8],
                    idx,
                    make_on_click("excluir", code),
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


def create_contratos_content(
    screen: Any,
    buyer_filter: Optional[str],
    seller_filter: Optional[str],
) -> ft.Control:
    """Conteúdo da aba Contratos com tabela em container e scroll."""
    buyer_value = (buyer_filter or "").strip()
    seller_value = (seller_filter or "").strip()

    contracts = list_contracts_for_table()

    def matches_filters(c: Dict[str, Any]) -> bool:
        contractor = str(c.get("contractor") or "")
        seller = str(c.get("service_provider") or "")
        if buyer_value and buyer_value.lower() not in contractor.lower():
            return False
        if seller_value and seller_value.lower() not in seller.lower():
            return False
        return True

    filtered_contracts = [c for c in contracts if matches_filters(c)]

    buyer_field = ft.TextField(
        label="Comprador",
        prefix_icon=ft.Icons.SEARCH,
        width=260,
        value=buyer_value,
    )

    seller_field = ft.TextField(
        label="Vendedor",
        prefix_icon=ft.Icons.SEARCH,
        width=260,
        value=seller_value,
    )

    def apply_filters(_: ft.ControlEvent) -> None:
        screen.navigation.go(
            "/comercializacao",
            params={
                "submenu": "contratos",
                "buyer": buyer_field.value,
                "seller": seller_field.value,
            },
        )

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

    new_contract_button = ft.ElevatedButton(
        text="Novo Contrato",
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
                "submenu": "contratos",
                "contracts_view": "new",
                "buyer": buyer_field.value,
                "seller": seller_field.value,
            },
        ),
    )

    actions_row = ft.Row(
        controls=[
            search_button,
            new_contract_button,
        ],
        spacing=12,
        alignment=ft.MainAxisAlignment.START,
    )

    table = _create_contracts_table(filtered_contracts, screen, buyer_value, seller_value)

    return ft.Container(
        expand=True,
        padding=20,
        content=ft.Column(
            controls=[
                filters_row,
                ft.Container(height=12),
                actions_row,
                ft.Container(height=16),
                table,
            ],
            spacing=6,
            alignment=ft.MainAxisAlignment.START,
        ),
    )

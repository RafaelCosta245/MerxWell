from typing import Any, Dict, Optional

import flet as ft

from scripts.comercializacao_service import (
    MONTH_LABELS,
    get_client_dashboard_data,
    list_contract_clients,
)


def _create_metric_summary(label: str, value: int) -> ft.Control:
    return ft.Container(
        padding=10,
        content=ft.Column(
            controls=[
                ft.Text(label, size=12, color=ft.Colors.GREY_700),
                ft.Text(str(value), size=22, weight=ft.FontWeight.BOLD),
            ],
            spacing=4,
            alignment=ft.MainAxisAlignment.START,
        ),
    )


def _create_empty_metrics_row() -> ft.Control:
    return ft.Row(
        controls=[
            ft.Text(
                "Nenhum cliente selecionado.",
                size=14,
                color=ft.Colors.GREY_700,
            )
        ],
    )


def _create_filters_row(
    screen: Any,
    clients: list[str],
    selected_client: Optional[str],
    energy_type: Optional[str],
    submarket: Optional[str],
    contract_type: Optional[str],
) -> tuple[ft.Control, Dict[str, Optional[str]]]:
    dropdown_width = 220

    allowed_clients = {"NOVO COM", "MERX", "FORTLEV SOLAR COM"}
    client_options_list = [c for c in clients if c in allowed_clients]

    client_dd = ft.Dropdown(
        label="Cliente",
        hint_text="Escolha um cliente...",
        options=[ft.dropdown.Option(c) for c in client_options_list],
        value=selected_client if selected_client in client_options_list else None,
        width=dropdown_width,
    )

    energy_dd = ft.Dropdown(
        label="Tipo de Energia",
        hint_text="Todos",
        options=[
            ft.dropdown.Option("I5"),
            ft.dropdown.Option("I1"),
            ft.dropdown.Option("I0"),
            ft.dropdown.Option("CONV"),
            ft.dropdown.Option("CQ5"),
        ],
        value=energy_type,
        width=dropdown_width,
    )

    submarket_dd = ft.Dropdown(
        label="Submercado",
        hint_text="Todos",
        options=[
            ft.dropdown.Option("SE/CO"),
            ft.dropdown.Option("NE"),
            ft.dropdown.Option("N"),
            ft.dropdown.Option("S"),
        ],
        value=submarket,
        width=dropdown_width,
    )

    contract_type_dd = ft.Dropdown(
        label="Modalidade",
        hint_text="Todas",
        options=[
            ft.dropdown.Option("ATACADISTA"),
            ft.dropdown.Option("VAREJISTA"),
            ft.dropdown.Option("AUTOPRODUÇÃO"),
        ],
        value=contract_type,
        width=dropdown_width,
    )

    def apply_filters(_: ft.ControlEvent) -> None:
        screen.navigation.go(
            "/comercializacao",
            params={
                "submenu": "visao",
                "client": client_dd.value,
                "energy_type": energy_dd.value,
                "submarket": submarket_dd.value,
                "contract_type": contract_type_dd.value,
            },
        )

    client_dd.on_change = apply_filters
    energy_dd.on_change = apply_filters
    submarket_dd.on_change = apply_filters
    contract_type_dd.on_change = apply_filters

    row = ft.Row(
        controls=[client_dd, energy_dd, submarket_dd, contract_type_dd],
        spacing=16,
        alignment=ft.MainAxisAlignment.START,
    )

    current_filters = {
        "energy_type": energy_type,
        "submarket": submarket,
        "contract_type": contract_type,
    }

    return row, current_filters


def _create_year_chart_card(year: int, year_data: Dict[str, Any]) -> ft.Control:
    months = list(year_data.get("months", MONTH_LABELS))
    buy_mwh = list(year_data.get("buy", []))
    sell_mwh = list(year_data.get("sell", []))

    while len(buy_mwh) < len(months):
        buy_mwh.append(0.0)
    while len(sell_mwh) < len(months):
        sell_mwh.append(0.0)

    hours_per_month = [
        744.0,
        672.0,
        744.0,
        720.0,
        744.0,
        720.0,
        744.0,
        744.0,
        720.0,
        744.0,
        720.0,
        744.0,
    ]

    buy_mwm: list[float] = []
    sell_mwm: list[float] = []
    diff_mwm: list[float] = []

    for i in range(len(months)):
        hours = hours_per_month[i] if i < len(hours_per_month) else 744.0
        b = float(buy_mwh[i] or 0.0) / hours if hours > 0 else 0.0
        s = float(sell_mwh[i] or 0.0) / hours if hours > 0 else 0.0
        d = b - s
        buy_mwm.append(b)
        sell_mwm.append(s)
        diff_mwm.append(d)

    max_volume = max(
        max((abs(v) for v in buy_mwm), default=0.0),
        max((abs(v) for v in sell_mwm), default=0.0),
        max((abs(v) for v in diff_mwm), default=0.0),
    ) or 1.0
    max_y = max_volume * 1.2

    buy_avg_price = float(year_data.get("buy_avg_price", 0.0) or 0.0)
    sell_avg_price = float(year_data.get("sell_avg_price", 0.0) or 0.0)

    bar_groups: list[ft.BarChartGroup] = []
    for i, label in enumerate(months):
        diff_value = diff_mwm[i]
        diff_color = (
            ft.Colors.RED_400 if diff_value < 0 else ft.Colors.AMBER_400
        )
        if diff_value > 0:
            diff_label = "Sobra"
        elif diff_value < 0:
            diff_label = "Déficit"
        else:
            diff_label = "Diferença"
        bar_groups.append(
            ft.BarChartGroup(
                x=i,
                bar_rods=[
                    ft.BarChartRod(
                        from_y=0,
                        to_y=buy_mwm[i],
                        width=10,
                        color=ft.Colors.GREEN_400,
                        tooltip=f"Compra: {buy_mwm[i]:.2f} MWm",
                        border_radius=4,
                    ),
                    ft.BarChartRod(
                        from_y=0,
                        to_y=sell_mwm[i],
                        width=10,
                        color=ft.Colors.BLUE_400,
                        tooltip=f"Venda: {sell_mwm[i]:.2f} MWm",
                        border_radius=4,
                    ),
                    ft.BarChartRod(
                        from_y=0,
                        to_y=abs(diff_value),
                        width=10,
                        color=diff_color,
                        tooltip=f"{diff_label} - {diff_value:.2f} MWm",
                        border_radius=4,
                    ),
                ],
                group_vertically=False,
            )
        )

    interval = max_y / 5 if max_y > 0 else 1

    bar_chart = ft.BarChart(
        bar_groups=bar_groups,
        border=ft.border.all(1, ft.Colors.GREY_300),
        left_axis=ft.ChartAxis(
            labels_size=40,
            title=ft.Text("Volume (MWm)", size=12, weight=ft.FontWeight.BOLD),
            title_size=30,
        ),
        bottom_axis=ft.ChartAxis(
            labels_size=28,
            labels=[
                ft.ChartAxisLabel(
                    value=i,
                    label=ft.Text(months[i], size=11, weight=ft.FontWeight.BOLD),
                )
                for i in range(len(months))
            ],
        ),
        horizontal_grid_lines=ft.ChartGridLines(
            interval=interval,
            color=ft.Colors.GREY_300,
            width=1,
        ),
        tooltip_bgcolor=ft.Colors.with_opacity(0.9, ft.Colors.GREY_800),
        max_y=max_y,
        min_y=0,
        expand=True,
    )

    def _format_price(label: str, value: float) -> str:
        if value <= 0:
            return f"{label} - Preço médio: N/A"
        return f"{label} - Preço médio: R$ {value:.2f}/MWh"

    has_positive_diff = any(d > 0 for d in diff_mwm)
    has_negative_diff = any(d < 0 for d in diff_mwm)

    diff_legend_items: list[ft.Control] = []
    if has_positive_diff:
        diff_legend_items.append(
            ft.Row(
                controls=[
                    ft.Container(
                        width=16,
                        height=16,
                        bgcolor=ft.Colors.AMBER_400,
                        border_radius=4,
                    ),
                    ft.Text("Sobra", size=11, color=ft.Colors.GREY_700),
                ],
                spacing=6,
            )
        )
    if has_negative_diff:
        diff_legend_items.append(
            ft.Row(
                controls=[
                    ft.Container(
                        width=16,
                        height=16,
                        bgcolor=ft.Colors.RED_400,
                        border_radius=4,
                    ),
                    ft.Text("Déficit", size=11, color=ft.Colors.GREY_700),
                ],
                spacing=6,
            )
        )

    legend_controls: list[ft.Control] = [
        ft.Row(
            controls=[
                ft.Container(
                    width=16,
                    height=16,
                    bgcolor=ft.Colors.GREEN_400,
                    border_radius=4,
                ),
                ft.Text(
                    _format_price("Compra", buy_avg_price),
                    size=11,
                    color=ft.Colors.GREY_700,
                ),
            ],
            spacing=6,
        ),
        ft.Row(
            controls=[
                ft.Container(
                    width=16,
                    height=16,
                    bgcolor=ft.Colors.BLUE_400,
                    border_radius=4,
                ),
                ft.Text(
                    _format_price("Venda", sell_avg_price),
                    size=11,
                    color=ft.Colors.GREY_700,
                ),
            ],
            spacing=6,
        ),
    ]

    legend_controls.extend(diff_legend_items)

    legend = ft.Row(
        controls=legend_controls,
        spacing=20,
        alignment=ft.MainAxisAlignment.CENTER,
    )

    return ft.Container(
        bgcolor=ft.Colors.WHITE,
        border_radius=10,
        padding=16,
        content=ft.Column(
            controls=[
                ft.Text(
                    f"{year} – Volume de Contratos por Mês ({year})",
                    size=16,
                    weight=ft.FontWeight.W_600,
                ),
                legend,
                ft.Container(
                    height=320,
                    content=bar_chart,
                ),
            ],
            spacing=8,
            alignment=ft.MainAxisAlignment.START,
        ),
    )


def _create_year_charts(client_name: str, years: Dict[int, Dict[str, Any]]) -> ft.Control:
    if not years:
        return ft.Container(
            padding=20,
            content=ft.Text(
                f"Nenhum contrato encontrado para o cliente {client_name}.",
                size=14,
                color=ft.Colors.GREY_700,
            ),
        )

    year_cards: list[ft.Control] = []
    for year in sorted(years.keys()):
        year_cards.append(_create_year_chart_card(year, years[year]))

    return ft.Column(
        controls=year_cards,
        spacing=24,
        alignment=ft.MainAxisAlignment.START,
    )


def create_portfolio_content(
    screen: Any,
    selected_client: Optional[str],
    energy_type: Optional[str],
    submarket: Optional[str],
    contract_type: Optional[str],
) -> ft.Control:
    clients = list_contract_clients()

    client_value = selected_client if selected_client in clients else None

    filters_row, current_filters = _create_filters_row(
        screen,
        clients,
        client_value,
        energy_type,
        submarket,
        contract_type,
    )

    if client_value:
        data = get_client_dashboard_data(
            client_value,
            energy_type=current_filters["energy_type"],
            submarket=current_filters["submarket"],
            contract_type=current_filters["contract_type"],
        )
        metrics_row = ft.Row(
            controls=[
                _create_metric_summary(
                    "Total de Contratos", int(data.get("total_contracts", 0))
                ),
                _create_metric_summary(
                    "Contratos Ativos", int(data.get("active_contracts", 0))
                ),
                _create_metric_summary(
                    "Contratos Inativos", int(data.get("inactive_contracts", 0))
                ),
            ],
            spacing=40,
            alignment=ft.MainAxisAlignment.START,
        )
        charts = _create_year_charts(client_value, data.get("years", {}))
    else:
        data = None
        metrics_row = _create_empty_metrics_row()
        charts = ft.Container(
            padding=20,
            content=ft.Text(
                "Selecione um cliente para visualizar os contratos.",
                size=14,
                color=ft.Colors.GREY_700,
            ),
        )

    return ft.Container(
        padding=20,
        expand=True,
        content=ft.Column(
            controls=[
                ft.Text(
                    "Dados de Contratos por Cliente",
                    size=20,
                    weight=ft.FontWeight.BOLD,
                ),
                filters_row,
                metrics_row,
                charts,
            ],
            spacing=20,
            alignment=ft.MainAxisAlignment.START,
        ),
    )

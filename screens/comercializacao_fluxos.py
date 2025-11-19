from typing import Any

import flet as ft


def _create_fluxo_chart_card(row_index: int, col_index: int) -> ft.Control:
    title = f"Fluxo {row_index + 1}-{col_index + 1}"

    return ft.Container(
        width=220,
        height=160,
        bgcolor=ft.Colors.BLUE_50,
        border_radius=10,
        padding=10,
        content=ft.Column(
            controls=[
                ft.Text(title, size=13, weight=ft.FontWeight.W_600),
                ft.Text(
                    "Gráfico de exemplo",
                    size=11,
                    color=ft.Colors.GREY_700,
                ),
                ft.Container(
                    expand=True,
                    bgcolor=ft.Colors.WHITE,
                    border_radius=6,
                    alignment=ft.alignment.center,
                    content=ft.Icon(
                        name=ft.Icons.SHOW_CHART,
                        color=ft.Colors.BLUE_400,
                        size=32,
                    ),
                ),
            ],
            spacing=6,
            alignment=ft.MainAxisAlignment.START,
        ),
    )


def create_fluxos_content(screen: Any) -> ft.Control:
    chart_rows: list[ft.Control] = []

    for row_index in range(4):
        row_controls: list[ft.Control] = []
        for col_index in range(6):
            row_controls.append(
                _create_fluxo_chart_card(
                    row_index=row_index,
                    col_index=col_index,
                )
            )
        chart_rows.append(ft.Row(controls=row_controls, spacing=16))

    return ft.Container(
        width=1600,
        height=1000,
        content=ft.Column(
            controls=chart_rows,
            spacing=16,
            alignment=ft.MainAxisAlignment.START,
        ),
    )

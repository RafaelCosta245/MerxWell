from typing import Any

import flet as ft


def _create_metric_card(
    title: str,
    subtitle: str,
    value: str,
    badge_text: str,
) -> ft.Control:
    return ft.Container(
        col=4,
        bgcolor=ft.Colors.BLUE_50,
        border_radius=10,
        padding=12,
        content=ft.Column(
            controls=[
                ft.Text(title, size=14, weight=ft.FontWeight.W_600),
                ft.Text(subtitle, size=12, color=ft.Colors.GREY_700),
                ft.Row(
                    controls=[
                        ft.Text(value, size=20, weight=ft.FontWeight.BOLD),
                        ft.Container(
                            padding=ft.padding.symmetric(horizontal=6, vertical=2),
                            border_radius=20,
                            bgcolor=ft.Colors.WHITE,
                            content=ft.Text(
                                badge_text,
                                size=12,
                                color=ft.Colors.GREEN_700,
                            ),
                        ),
                    ],
                    alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                ),
            ],
            spacing=6,
            alignment=ft.MainAxisAlignment.START,
        ),
    )


def create_visao_geral_content(screen: Any) -> ft.Control:
    row1 = ft.ResponsiveRow(
        controls=[
            _create_metric_card(
                title="Revenue This Month",
                subtitle="Receita acumulada",
                value="R$ 1.5M",
                badge_text="+8%",
            ),
            _create_metric_card(
                title="Operational Efficiency",
                subtitle="Eficiência operacional",
                value="85%",
                badge_text="Meta 80%",
            ),
            _create_metric_card(
                title="Client Metrics",
                subtitle="Indicadores de clientes",
                value="120%",
                badge_text="Crescimento",
            ),
        ],
        run_spacing=12,
    )

    row2 = ft.ResponsiveRow(
        controls=[
            _create_metric_card(
                title="Energy Atoms",
                subtitle="Energia contratada",
                value="2.7M",
                badge_text="Estável",
            ),
            _create_metric_card(
                title="Energy Flow (MW)",
                subtitle="Fluxo de energia",
                value="56 MW",
                badge_text="Normal",
            ),
            _create_metric_card(
                title="Market Price (R$/MWh)",
                subtitle="Preço médio",
                value="R$ 350",
                badge_text="+5%",
            ),
        ],
        run_spacing=12,
    )

    return ft.Container(
        expand=True,
        content=ft.Column(
            controls=[row1, row2],
            spacing=16,
            alignment=ft.MainAxisAlignment.START,
        ),
    )

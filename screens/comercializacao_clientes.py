from typing import Any

import flet as ft


def create_clientes_content(screen: Any) -> ft.Control:
    return ft.Container(
        expand=True,
        content=ft.Column(
            controls=[
                ft.Text("Clientes", size=18, weight=ft.FontWeight.W_600),
                ft.Text(
                    "Lista e detalhes dos clientes atendidos.",
                    size=14,
                    color=ft.Colors.GREY_700,
                ),
            ],
            spacing=8,
            alignment=ft.MainAxisAlignment.START,
        ),
    )

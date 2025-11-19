from typing import Any

import flet as ft


def create_produtos_content(screen: Any) -> ft.Control:
    return ft.Container(
        expand=True,
        content=ft.Column(
            controls=[
                ft.Text("Produtos", size=18, weight=ft.FontWeight.W_600),
                ft.Text(
                    "Catálogo de produtos e estruturas comerciais.",
                    size=14,
                    color=ft.Colors.GREY_700,
                ),
            ],
            spacing=8,
            alignment=ft.MainAxisAlignment.START,
        ),
    )

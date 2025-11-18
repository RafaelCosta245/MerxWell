from typing import Any, Dict, Optional

import flet as ft

from screens import BaseScreen


class HomeScreen(BaseScreen):
    """Tela inicial da aplicação."""

    route: str = "/home"

    def create_header(self) -> ft.Control:
        """Cria o cabeçalho da tela inicial."""
        return ft.AppBar(
            title=ft.Text("Tela inicial"),
            center_title=True,
        )

    def create_content(self, params: Optional[Dict[str, Any]] = None) -> ft.Control:
        """Cria o conteúdo principal da tela inicial."""
        description = ft.Text(
            "Este é um exemplo de aplicação desktop com Flet, "
            "navegação baseada em Views e telas modulares.",
            size=16,
        )

        go_example_button = ft.ElevatedButton(
            text="Ir para tela de exemplo",
            on_click=lambda _: self.navigation.go(
                "/exemplo", params={"mensagem": "Olá a partir da Home!"}
            ),
        )

        return ft.Container(
            padding=20,
            content=ft.Column(
                controls=[
                    description,
                    ft.Text("Use os botões abaixo para navegar entre as telas."),
                    go_example_button,
                ],
                spacing=16,
                alignment=ft.MainAxisAlignment.START,
            ),
        )

    def create_footer(self) -> ft.Control:
        """Cria o rodapé da tela inicial."""
        return ft.Container(
            padding=10,
            alignment=ft.alignment.center,
            content=ft.Text(
                "Rodapé - Tela inicial",
                size=12,
                color=ft.Colors.GREY,
            ),
        )

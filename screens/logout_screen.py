from typing import Any, Dict, Optional

import flet as ft

from screens import BaseScreen


class LogoutScreen(BaseScreen):
    route: str = "/logout"

    def create_header(self) -> ft.Control:
        return self._create_header_container()

    def create_content(self, params: Optional[Dict[str, Any]] = None) -> ft.Control:
        return self._create_content_container()

    def create_footer(self) -> ft.Control:
        return self._create_footer_container()

    def _create_header_icon(self) -> ft.Control:
        return ft.Icon(name=ft.Icons.LOGOUT, color=ft.Colors.RED, size=28)

    def _create_header_title(self) -> ft.Control:
        return ft.Text("Logout", size=22, weight=ft.FontWeight.BOLD)

    def _create_header_container(self) -> ft.Control:
        return ft.Container(
            padding=10,
            content=ft.Row(
                controls=[self._create_header_icon(), self._create_header_title()],
                alignment=ft.MainAxisAlignment.START,
                spacing=10,
            ),
        )

    def _create_content_title(self) -> ft.Control:
        return ft.Text("Sair da aplicação", size=18, weight=ft.FontWeight.W_600)

    def _create_content_description(self) -> ft.Control:
        return ft.Text(
            "Confirme o logout ou implemente aqui o fluxo de autenticação.",
            size=14,
        )

    def _create_content_container(self) -> ft.Control:
        return ft.Container(
            padding=20,
            content=ft.Column(
                controls=[self._create_content_title(), self._create_content_description()],
                spacing=8,
                alignment=ft.MainAxisAlignment.START,
            ),
        )

    def _create_footer_container(self) -> ft.Control:
        return ft.Container(
            padding=10,
            alignment=ft.alignment.center,
            content=ft.Text(
                "Rodapé - Logout",
                size=12,
                color=ft.Colors.GREY,
            ),
        )

from typing import Any, Dict, Optional

import flet as ft

from screens import BaseScreen
from helpers.storage import get_output_directory, prompt_folder_selection


class BackofficeScreen(BaseScreen):
    route: str = "/backoffice"

    def create_header(self) -> ft.Control:
        return self._create_header_container()

    def create_content(self, params: Optional[Dict[str, Any]] = None) -> ft.Control:
        return self._create_content_container()

    def create_footer(self) -> ft.Control:
        return self._create_footer_container()

    def _create_header_icon(self) -> ft.Control:
        return ft.Icon(name=ft.Icons.BUSINESS_CENTER, color=ft.Colors.BLUE, size=28)

    def _create_header_title(self) -> ft.Control:
        return ft.Text("Backoffice", size=22, weight=ft.FontWeight.BOLD)

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
        return ft.Text("Área de Backoffice", size=18, weight=ft.FontWeight.W_600)

    def _create_content_description(self) -> ft.Control:
        return ft.Text(
            "Tela básica de Backoffice. Adicione aqui os componentes e ações dessa área.",
            size=14,
        )

    def _create_output_directory_section(self) -> ft.Control:
        """Create section to display and change output directory."""
        current_dir = get_output_directory(self.page)
        
        dir_text = ft.Text(
            value=current_dir or "Nenhuma pasta configurada",
            size=12,
            color=ft.Colors.GREY_700,
            weight=ft.FontWeight.W_400,
        )
        
        def on_change_folder(_):
            def on_selected(new_path: str):
                dir_text.value = new_path
                dir_text.update()
            
            prompt_folder_selection(self.page, on_selected=on_selected)
        
        return ft.Container(
            padding=20,
            border=ft.border.all(1, ft.Colors.GREY_300),
            border_radius=8,
            bgcolor=ft.Colors.GREY_50,
            content=ft.Column(
                controls=[
                    ft.Text(
                        "Pasta de Saída de Arquivos",
                        size=16,
                        weight=ft.FontWeight.BOLD,
                        color=ft.Colors.BLUE_700,
                    ),
                    ft.Container(height=8),
                    ft.Row(
                        controls=[
                            ft.Icon(ft.Icons.FOLDER_OPEN, size=20, color=ft.Colors.BLUE_600),
                            ft.Text("Pasta atual:", size=13, weight=ft.FontWeight.W_500),
                        ],
                        spacing=8,
                    ),
                    dir_text,
                    ft.Container(height=12),
                    ft.ElevatedButton(
                        text="Alterar Pasta de Saída",
                        icon=ft.Icons.FOLDER,
                        on_click=on_change_folder,
                        bgcolor=ft.Colors.BLUE_600,
                        color=ft.Colors.WHITE,
                        style=ft.ButtonStyle(
                            shape=ft.RoundedRectangleBorder(radius=6),
                        ),
                    ),
                    ft.Container(height=8),
                    ft.Text(
                        "💡 Esta pasta será usada para salvar todos os documentos gerados (propostas, contratos, etc.)",
                        size=11,
                        color=ft.Colors.GREY_600,
                        italic=True,
                    ),
                ],
                spacing=4,
            ),
        )

    def _create_content_container(self) -> ft.Control:
        return ft.Container(
            padding=20,
            content=ft.Column(
                controls=[
                    self._create_content_title(),
                    self._create_content_description(),
                    ft.Container(height=20),
                    self._create_output_directory_section(),
                ],
                spacing=8,
                alignment=ft.MainAxisAlignment.START,
            ),
        )

    def _create_footer_container(self) -> ft.Control:
        return ft.Container(
            padding=10,
            alignment=ft.alignment.center,
            content=ft.Text(
                "Rodapé - Backoffice",
                size=12,
                color=ft.Colors.GREY,
            ),
        )


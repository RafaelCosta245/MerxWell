from typing import Any, Dict, Optional

import flet as ft

from screens import BaseScreen
from scripts import exemplo_script


class ExemploScreen(BaseScreen):
    """Tela de exemplo, utilizada para demonstrar navegação com parâmetros."""

    route: str = "/exemplo"

    def create_header(self) -> ft.Control:
        """Cria o cabeçalho da tela de exemplo."""
        return ft.AppBar(
            title=ft.Text("Tela de exemplo"),
            center_title=True,
            leading=ft.IconButton(
                icon=ft.Icons.ARROW_BACK,
                on_click=lambda _: self.navigation.back(),
            ),
        )

    def create_content(self, params: Optional[Dict[str, Any]] = None) -> ft.Control:
        """Cria o conteúdo principal da tela de exemplo."""
        params = params or {}
        mensagem_param = params.get("mensagem", "Sem mensagem recebida.")

        resultado_script = exemplo_script.processar_exemplo(mensagem_param)

        voltar_button = ft.ElevatedButton(
            text="Voltar para Home",
            on_click=lambda _: self.navigation.back(),
        )

        ir_home_button = ft.TextButton(
            text="Ir para Home (go)",
            on_click=lambda _: self.navigation.go("/home"),
        )

        return ft.Container(
            padding=20,
            content=ft.Column(
                controls=[
                    ft.Text("Parâmetros recebidos pela navegação:", size=16),
                    ft.Text(str(params)),
                    ft.Divider(),
                    ft.Text("Resultado do script de exemplo:", size=16),
                    ft.Text(resultado_script),
                    ft.Divider(),
                    voltar_button,
                    ir_home_button,
                ],
                spacing=12,
                alignment=ft.MainAxisAlignment.START,
            ),
        )

    def create_footer(self) -> ft.Control:
        """Cria o rodapé da tela de exemplo."""
        return ft.Container(
            padding=10,
            alignment=ft.alignment.center,
            content=ft.Text(
                "Rodapé - Tela de exemplo",
                size=12,
                color=ft.Colors.GREY,
            ),
        )

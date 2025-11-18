import flet as ft
import os

from config.navigation import create_navigation


def main(page: ft.Page) -> None:
    """Função principal da aplicação Flet desktop.

    Configura a janela, inicializa o gerenciador de navegação e
    direciona a aplicação para a rota inicial.
    """
    page.title = "MerxWell"
    page.window.icon = os.path.abspath("assets/icons/LogoMerx256.ico")
    page.window_width = 1024
    page.window_height = 768
    page.window_resizable = True
    page.theme_mode = ft.ThemeMode.LIGHT

    navigation = create_navigation(page)

    # Usa a rota atual caso exista, senão navega para o backoffice.
    initial_route = page.route or "/backoffice"
    navigation.go(initial_route)


if __name__ == "__main__":
    # Executa a aplicação Flet em modo desktop
    ft.app(target=main, view=ft.AppView.FLET_APP)

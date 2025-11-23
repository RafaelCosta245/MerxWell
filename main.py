import flet as ft
import os

from config.navigation import create_navigation
from helpers.paths import get_icon_path
from helpers.storage import ensure_output_directory_configured


def main(page: ft.Page) -> None:
    """Função principal da aplicação Flet desktop.

    Configura a janela, inicializa o gerenciador de navegação e
    direciona a aplicação para a rota inicial.
    """
    page.title = "MerxWell"
    page.window.icon = get_icon_path("LogoMerx256.ico")
    page.window_width = 1024
    page.window_height = 768
    page.window_resizable = True
    page.theme_mode = ft.ThemeMode.LIGHT

    navigation = create_navigation(page)

    # Ensure output directory is configured before proceeding
    def on_directory_configured(directory_path: str):
        print(f"[MAIN] Output directory configured: {directory_path}")
        # Navigate to initial route after directory is configured
        initial_route = page.route or "/backoffice"
        navigation.go(initial_route)
    
    # Check if directory is configured, if not, prompt user
    if not ensure_output_directory_configured(page, on_configured=on_directory_configured):
        # Will prompt user for directory, navigation happens in callback
        pass
    else:
        # Already configured, navigate immediately
        initial_route = page.route or "/backoffice"
        navigation.go(initial_route)


if __name__ == "__main__":
    # Executa a aplicação Flet em modo desktop
    ft.app(target=main, view=ft.AppView.FLET_APP)

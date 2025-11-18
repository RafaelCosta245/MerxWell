from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any, Dict, Optional, TYPE_CHECKING

import flet as ft

if TYPE_CHECKING:  # Evita dependência circular em tempo de execução
    from config.navigation import NavigationManager


class BaseScreen(ABC):
    """Classe base para todas as telas da aplicação.

    Cada tela específica deve herdar desta classe e implementar os métodos
    de criação de cabeçalho, conteúdo e rodapé.
    """

    # Rota associada à tela. Deve ser sobrescrita nas subclasses.
    route: str = "/"

    def __init__(self, page: ft.Page, navigation: "NavigationManager") -> None:
        self.page = page
        self.navigation = navigation

    @abstractmethod
    def create_header(self) -> ft.Control:
        """Cria o componente de cabeçalho da tela."""

    @abstractmethod
    def create_content(self, params: Optional[Dict[str, Any]] = None) -> ft.Control:
        """Cria o componente de conteúdo principal da tela."""

    def create_footer(self) -> ft.Control:
        """Cria o componente de rodapé da tela.

        Implementação padrão retorna um container vazio. As telas podem
        sobrescrever este método para definir um rodapé específico ou
        simplesmente não sobrescrever para não exibir nada relevante.
        """
        return ft.Container()

    def build(self, params: Optional[Dict[str, Any]] = None) -> ft.Control:
        """Monta a View da tela a partir de cabeçalho, conteúdo e rodapé.

        O cabeçalho pode ser um AppBar ou qualquer outro controle. Quando
        for um AppBar, ele será atribuído à propriedade `appbar` da View;
        caso contrário, será inserido como primeiro controle da tela.
        """
        header = self.create_header()
        content = self.create_content(params=params)
        footer = self.create_footer()

        return ft.Column(
            controls=[header, content, footer],
            spacing=0,
            expand=True,
        )

"""Gerenciador centralizado de navegação baseado em Views do Flet.

Permite registrar novas telas de forma simples e oferece métodos para
navegar entre rotas com suporte a histórico (voltar/avançar).
"""

from __future__ import annotations

from typing import Any, Dict, List, Optional, Tuple, Type
from urllib.parse import parse_qs, urlencode, urlparse

import flet as ft

from screens import BaseScreen
from screens.home_screen import HomeScreen
from screens.exemplo_screen import ExemploScreen
from screens.navbar import NavBar
from screens.backoffice_screen import BackofficeScreen
from screens.comercializacao_screen import ComercializacaoScreen
from screens.financeiro_screen import FinanceiroScreen
from screens.banco_de_dados_screen import BancoDeDadosScreen
from screens.emails_screen import EmailsScreen
from screens.relatorios_screen import RelatoriosScreen
from screens.simulador_screen import SimuladorScreen
from screens.logout_screen import LogoutScreen


class NavigationManager:
    """Gerencia a navegação da aplicação usando Views do Flet."""

    def __init__(self, page: ft.Page) -> None:
        self.page = page
        self._routes: Dict[str, Type[BaseScreen]] = {}
        self._default_route: str = "/backoffice"
        self._history: List[Tuple[str, Dict[str, Any]]] = []
        self._future: List[Tuple[str, Dict[str, Any]]] = []
        self._current_route: str = self._default_route
        self._current_params: Dict[str, Any] = {}
        self._content_container: Optional[ft.Container] = None
        self._root_column: Optional[ft.Column] = None

    def register_route(
        self,
        route: str,
        screen_cls: Type[BaseScreen],
        *,
        default: bool = False,
    ) -> None:
        """Registra uma rota associando-a a uma classe de tela."""
        self._routes[route] = screen_cls
        if default:
            self._default_route = route

    def attach_layout(self, root: ft.Column, content_container: ft.Container) -> None:
        """Associa o layout raiz e o container de conteúdo ao gerenciador."""
        self._root_column = root
        self._content_container = content_container

    # ------------------------------------------------------------------
    # Integração com a NavBar
    # ------------------------------------------------------------------
    def handle_nav(self, nav_key: str) -> None:
        """Callback chamado pela NavBar ao clicar em um item."""
        if not nav_key:
            return
        route = nav_key if nav_key.startswith("/") else f"/{nav_key}"
        self.go(route)

    # ------------------------------------------------------------------
    # API pública de navegação
    # ------------------------------------------------------------------
    def go(self, route: str, params: Optional[Dict[str, Any]] = None) -> None:
        """Navega para a rota informada, registrando no histórico e atualizando o conteúdo."""
        if not route:
            route = self._default_route

        params = params or {}
        self._history.append((route, params))
        self._future.clear()

        self._current_route = route
        self._current_params = params
        self._show_route(route, params)

    def back(self) -> None:
        """Volta para a rota anterior no histórico, se existir."""
        if len(self._history) <= 1:
            return

        current = self._history.pop()
        self._future.append(current)

        route, params = self._history[-1]
        self._current_route = route
        self._current_params = params
        self._show_route(route, params)

    def forward(self) -> None:
        """Avança uma posição no histórico, se possível."""
        if not self._future:
            return

        route, params = self._future.pop()
        self._history.append((route, params))
        self._current_route = route
        self._current_params = params
        self._show_route(route, params)

    # ------------------------------------------------------------------
    # Implementação interna
    # ------------------------------------------------------------------
    def _build_view(self, route: str, params: Dict[str, Any]) -> Optional[ft.Control]:
        screen_cls = self._routes.get(route)
        if screen_cls is None:
            return None

        screen = screen_cls(self.page, self)
        return screen.build(params=params)

    def _show_route(self, route: str, params: Dict[str, Any]) -> None:
        """Atualiza apenas o conteúdo abaixo da NavBar, mantendo-a fixa."""
        if self._content_container is None or self._root_column is None:
            return

        content = self._build_view(route, params)
        if content is None:
            # Fallback para rota padrão
            route = self._default_route
            params = {}
            content = self._build_view(route, params)
            if content is None:
                return

        # Atualiza o container de conteúdo
        self._content_container.content = content

        # Atualiza a NavBar com o item selecionado
        if route in ("/", ""):
            selected_nav = "backoffice"
        else:
            selected_nav = route.lstrip("/")

        self._root_column.controls[0] = NavBar(
            on_nav=self.handle_nav,
            selected_nav=selected_nav,
        )

        self.page.update()

    @staticmethod
    def _parse_route(raw_route: str) -> Tuple[str, Dict[str, Any]]:
        parsed = urlparse(raw_route or "/")
        base_route = parsed.path or "/"
        raw_params = parse_qs(parsed.query)
        params: Dict[str, Any] = {
            key: values[0] if len(values) == 1 else values
            for key, values in raw_params.items()
        }
        return base_route, params

    @staticmethod
    def _build_route_string(route: str, params: Dict[str, Any]) -> str:
        if not params:
            return route
        return f"{route}?{urlencode(params)}"


def create_navigation(page: ft.Page) -> NavigationManager:
    """Cria o gerenciador de navegação e registra as rotas padrão.

    Para adicionar uma nova tela, basta:

    1. Criar o arquivo em `screens/` herdando de `BaseScreen`.
    2. Registrar a rota aqui utilizando `register_route`.
    """
    navigation = NavigationManager(page)

    # Rotas padrão
    navigation.register_route("/home", HomeScreen)
    navigation.register_route("/", BackofficeScreen, default=True)
    navigation.register_route("/exemplo", ExemploScreen)

    # Rotas da navbar principal
    navigation.register_route("/backoffice", BackofficeScreen)
    navigation.register_route("/comercializacao", ComercializacaoScreen)
    navigation.register_route("/financeiro", FinanceiroScreen)
    navigation.register_route("/banco_de_dados", BancoDeDadosScreen)
    navigation.register_route("/emails", EmailsScreen)
    navigation.register_route("/relatorios", RelatoriosScreen)
    navigation.register_route("/simulador", SimuladorScreen)
    navigation.register_route("/logout", LogoutScreen)

    # Layout raiz: NavBar fixa no topo + container de conteúdo abaixo
    content_container = ft.Container(expand=True)

    root_column = ft.Column(
        controls=[
            NavBar(on_nav=navigation.handle_nav, selected_nav="backoffice"),
            content_container,
        ],
        spacing=0,
        expand=True,
    )

    page.controls.clear()
    page.controls.append(root_column)

    navigation.attach_layout(root_column, content_container)

    return navigation

from typing import Any, Dict, Optional
import flet as ft
from screens import BaseScreen
from scripts.comercializacao_service import (
    MONTH_LABELS,
    get_client_dashboard_data,
    list_contract_clients,
)


class ComercializacaoScreen(BaseScreen):
    route: str = "/comercializacao"

    def create_header(self) -> ft.Control:
        return self._create_header_container()

    def create_content(self, params: Optional[Dict[str, Any]] = None) -> ft.Control:
        """Cria o conteúdo principal da tela de Comercialização.

        Nesta tela, temos uma coluna de submenus fixa à esquerda, que
        controla o conteúdo exibido à direita. O submenu selecionado é
        definido via parâmetro de navegação "submenu".
        """
        params = params or {}
        selected_submenu = params.get("submenu", "visao")
        selected_client = params.get("client")

        return self._create_main_content(selected_submenu, selected_client)

    # def create_footer(self) -> ft.Control:
    #     return self._create_footer_container()

    def _create_header_icon(self) -> ft.Control:
        return ft.Icon(name=ft.Icons.TRENDING_UP, color=ft.Colors.GREEN, size=28)

    def _create_header_title(self) -> ft.Control:
        return ft.Text("Comercialização", size=22, weight=ft.FontWeight.BOLD)

    def _create_header_container(self) -> ft.Control:
        return ft.Container(
            padding=10,
            content=ft.Row(
                controls=[self._create_header_icon(), self._create_header_title()],
                alignment=ft.MainAxisAlignment.START,
                spacing=10,
            ),
        )

    def _create_main_content(
        self,
        selected_submenu: str,
        selected_client: Optional[str],
    ) -> ft.Control:
        """Cria o layout principal com submenu à esquerda e conteúdo à direita."""
        return ft.Container(
            padding=2,
            expand=True,
            content=ft.Row(
                controls=[
                    self._create_submenu_column(selected_submenu),
                    self._create_subcontent_area(selected_submenu, selected_client),
                ],
                spacing=20,
                vertical_alignment=ft.CrossAxisAlignment.START,
            ),
        )

    # ------------------------------------------------------------------
    # Submenus
    # ------------------------------------------------------------------
    def _create_submenu_items(self) -> list[tuple[str, str, str]]:
        """Retorna a definição dos submenus da área de Comercialização."""
        return [
            ("Visão", "visao", ft.Icons.INSIGHTS),
            ("Visão Geral", "visao_geral", ft.Icons.DASHBOARD),
            ("Fluxos", "fluxos", ft.Icons.TIMELINE),
            ("Contratos", "contratos", ft.Icons.DESCRIPTION),
            ("Clientes", "clientes", ft.Icons.PEOPLE),
            ("Produtos", "produtos", ft.Icons.SHOPPING_BAG),
        ]

    def _create_submenu_button(
        self,
        label: str,
        key: str,
        icon_name: str,
        selected_submenu: str,
    ) -> ft.Control:
        """Cria um botão individual de submenu."""
        is_selected = key == selected_submenu

        return ft.TextButton(
            content=ft.Row(
                controls=[
                    ft.Icon(
                        name=icon_name,
                        size=18,
                        color=ft.Colors.BLUE_700 if is_selected else ft.Colors.GREY_700,
                    ),
                    ft.Text(
                        label,
                        size=14,
                        weight=ft.FontWeight.W_500 if is_selected else ft.FontWeight.NORMAL,
                        color=ft.Colors.BLUE_800 if is_selected else ft.Colors.GREY_800,
                    ),
                ],
                spacing=10,
                alignment=ft.MainAxisAlignment.START,
            ),
            style=ft.ButtonStyle(
                padding=ft.padding.symmetric(horizontal=12, vertical=6),
                bgcolor=ft.Colors.BLUE_50 if is_selected else ft.Colors.TRANSPARENT,
                shape=ft.RoundedRectangleBorder(radius=8),
            ),
            on_click=lambda _: self.navigation.go(
                "/comercializacao", params={"submenu": key}
            ),
        )

    def _create_submenu_column(self, selected_submenu: str) -> ft.Control:
        """Cria a coluna fixa de submenus da Comercialização."""
        submenu_controls: list[ft.Control] = []

        for label, key, icon_name in self._create_submenu_items():
            submenu_controls.append(
                self._create_submenu_button(label, key, icon_name, selected_submenu)
            )

        return ft.Container(
            width=230,
            bgcolor=ft.Colors.WHITE,
            border_radius=10,
            padding=15,
            content=ft.Column(
                controls=submenu_controls,
                spacing=4,
                alignment=ft.MainAxisAlignment.START,
            ),
        )

    # ------------------------------------------------------------------
    # Conteúdo das subtelas
    # ------------------------------------------------------------------
    def _create_subcontent_area(
        self,
        selected_submenu: str,
        selected_client: Optional[str],
    ) -> ft.Control:
        """Seleciona o conteúdo de acordo com o submenu escolhido."""
        if selected_submenu == "visao":
            inner = self._create_visao_dashboard(selected_client)
        elif selected_submenu == "visao_geral":
            inner = self._create_dashboard_content()
        elif selected_submenu == "fluxos":
            inner = self._create_fluxos_content()
        elif selected_submenu == "contratos":
            inner = self._create_contratos_content()
        elif selected_submenu == "clientes":
            inner = self._create_clientes_content()
        elif selected_submenu == "produtos":
            inner = self._create_produtos_content()
        else:
            # Fallback
            inner = self._create_dashboard_content()

        return self._wrap_in_scrollable_area(inner)

    def _wrap_in_scrollable_area(self, inner: ft.Control) -> ft.Control:
        """Envolve o conteúdo em uma área rolável vertical e horizontal.

        Apenas a área de conteúdo (à direita da coluna de submenus) terá
        scroll, mantendo navbar e submenus fixos.
        """
        return ft.Container(
            expand=True,
            content=ft.Column(
                expand=True,
                scroll=ft.ScrollMode.ALWAYS,
                controls=[inner],
            ),
        )

    # ------------------------------------------------------------------
    # Visão - Dashboard por cliente
    # ------------------------------------------------------------------
    def _create_visao_dashboard(self, selected_client: Optional[str]) -> ft.Control:
        """Cria o dashboard de contratos por cliente.

        Exibe um filtro de cliente, métricas agregadas e gráficos por ano
        com volumes de compra e venda por mês.
        """
        clients = list_contract_clients()

        client_value = selected_client if selected_client in clients else None

        client_filter = self._create_client_filter(clients, client_value)

        if client_value:
            data = get_client_dashboard_data(client_value)
            print(
                "[ComercializacaoScreen] Dados do serviço",
                {
                    "client": client_value,
                    "total_contracts": data.get("total_contracts"),
                    "active_contracts": data.get("active_contracts"),
                    "inactive_contracts": data.get("inactive_contracts"),
                    "years_keys": sorted(data.get("years", {}).keys()),
                },
            )
            metrics_row = self._create_client_metrics_row(data)
            charts = self._create_year_charts(client_value, data.get("years", {}))
        else:
            data = None
            metrics_row = self._create_empty_metrics_row()
            charts = self._create_empty_state(
                "Selecione um cliente para visualizar os contratos.",
            )

        return ft.Container(
            padding=20,
            expand=True,
            content=ft.Column(
                controls=[
                    ft.Text(
                        "Dados de Contratos por Cliente",
                        size=20,
                        weight=ft.FontWeight.BOLD,
                    ),
                    client_filter,
                    metrics_row,
                    charts,
                ],
                spacing=20,
                alignment=ft.MainAxisAlignment.START,
            ),
        )

    def _create_client_filter(
        self,
        clients: list[str],
        selected_client: Optional[str],
    ) -> ft.Control:
        """Cria o filtro de seleção de cliente."""
        options = [ft.dropdown.Option(c) for c in clients]

        def on_change(e: ft.ControlEvent) -> None:
            value = e.control.value
            self.navigation.go(
                "/comercializacao",
                params={"submenu": "visao", "client": value},
            )

        return ft.Dropdown(
            label="Selecionar Cliente",
            hint_text="Escolha um cliente...",
            options=options,
            value=selected_client,
            width=320,
            on_change=on_change,
        )

    def _create_client_metrics_row(self, data: Dict[str, Any]) -> ft.Control:
        """Exibe métricas agregadas de contratos do cliente."""
        total_contracts = int(data.get("total_contracts", 0))
        active_contracts = int(data.get("active_contracts", 0))
        inactive_contracts = int(data.get("inactive_contracts", 0))

        return ft.Row(
            controls=[
                self._create_metric_summary("Total de Contratos", total_contracts),
                self._create_metric_summary("Contratos Ativos", active_contracts),
                self._create_metric_summary("Contratos Inativos", inactive_contracts),
            ],
            spacing=40,
            alignment=ft.MainAxisAlignment.START,
        )

    def _create_metric_summary(self, label: str, value: int) -> ft.Control:
        """Cria um pequeno card de métrica resumida."""
        return ft.Container(
            padding=10,
            content=ft.Column(
                controls=[
                    ft.Text(label, size=12, color=ft.Colors.GREY_700),
                    ft.Text(str(value), size=22, weight=ft.FontWeight.BOLD),
                ],
                spacing=4,
                alignment=ft.MainAxisAlignment.START,
            ),
        )

    def _create_empty_metrics_row(self) -> ft.Control:
        """Layout exibido quando nenhum cliente foi selecionado."""
        return ft.Row(
            controls=[
                ft.Text(
                    "Nenhum cliente selecionado.",
                    size=14,
                    color=ft.Colors.GREY_700,
                )
            ],
        )

    def _create_year_charts(
        self,
        client_name: str,
        years: Dict[int, Dict[str, Any]],
    ) -> ft.Control:
        """Cria gráficos por ano de compra/venda."""
        if not years:
            print(
                "[ComercializacaoScreen] Nenhum ano disponível para",
                client_name,
            )
            return self._create_empty_state(
                f"Nenhum contrato encontrado para o cliente {client_name}.",
            )

        print(
            "[ComercializacaoScreen] Montando gráficos",
            {
                "client": client_name,
                "years": sorted(years.keys()),
                "buy_totals": {
                    year: sum(years[year].get("buy", [])) for year in years
                },
                "sell_totals": {
                    year: sum(years[year].get("sell", [])) for year in years
                },
            },
        )

        year_cards: list[ft.Control] = []

        for year in sorted(years.keys()):
            year_cards.append(self._create_year_chart_card(year, years[year]))

        return ft.Column(
            controls=year_cards,
            spacing=24,
            alignment=ft.MainAxisAlignment.START,
        )

    def _create_year_chart_card(self, year: int, year_data: Dict[str, Any]) -> ft.Control:
        """Cria o card com gráfico de barras duplas para um ano específico.

        Usa ft.BarChart com duas barras por mês (compra e venda) lado a
        lado, inspirado no exemplo de instructions/charts.py.
        """
        months = list(year_data.get("months", MONTH_LABELS))
        buy = list(year_data.get("buy", []))
        sell = list(year_data.get("sell", []))

        # Garante que as listas tenham pelo menos o tamanho de months
        while len(buy) < len(months):
            buy.append(0.0)
        while len(sell) < len(months):
            sell.append(0.0)

        max_volume = max(max(buy, default=0.0), max(sell, default=0.0)) or 1.0
        max_y = max_volume * 1.2

        print(
            "[ComercializacaoScreen] Ano",
            year,
            {
                "buy": buy,
                "sell": sell,
            },
        )

        bar_groups: list[ft.BarChartGroup] = []
        for i, label in enumerate(months):
            bar_groups.append(
                ft.BarChartGroup(
                    x=i,
                    bar_rods=[
                        ft.BarChartRod(
                            from_y=0,
                            to_y=buy[i],
                            width=12,
                            color=ft.Colors.GREEN_400,
                            tooltip=f"Compra: {buy[i]:.2f}",
                            border_radius=4,
                        ),
                        ft.BarChartRod(
                            from_y=0,
                            to_y=sell[i],
                            width=12,
                            color=ft.Colors.BLUE_400,
                            tooltip=f"Venda: {sell[i]:.2f}",
                            border_radius=4,
                        ),
                    ],
                    group_vertically=False,
                )
            )

        interval = max_y / 5 if max_y > 0 else 1

        bar_chart = ft.BarChart(
            bar_groups=bar_groups,
            border=ft.border.all(1, ft.Colors.GREY_300),
            left_axis=ft.ChartAxis(
                labels_size=40,
                title=ft.Text("Volume (MWh)", size=12, weight=ft.FontWeight.BOLD),
                title_size=30,
            ),
            bottom_axis=ft.ChartAxis(
                labels_size=28,
                labels=[
                    ft.ChartAxisLabel(
                        value=i,
                        label=ft.Text(months[i], size=11, weight=ft.FontWeight.BOLD),
                    )
                    for i in range(len(months))
                ],
            ),
            horizontal_grid_lines=ft.ChartGridLines(
                interval=interval,
                color=ft.Colors.GREY_300,
                width=1,
            ),
            tooltip_bgcolor=ft.Colors.with_opacity(0.9, ft.Colors.GREY_800),
            max_y=max_y,
            min_y=0,
            expand=True,
        )

        # Legenda simples compra/venda
        legend = ft.Row(
            controls=[
                ft.Row(
                    controls=[
                        ft.Container(
                            width=16,
                            height=16,
                            bgcolor=ft.Colors.GREEN_400,
                            border_radius=4,
                        ),
                        ft.Text("Compra", size=12),
                    ],
                    spacing=6,
                ),
                ft.Row(
                    controls=[
                        ft.Container(
                            width=16,
                            height=16,
                            bgcolor=ft.Colors.BLUE_400,
                            border_radius=4,
                        ),
                        ft.Text("Venda", size=12),
                    ],
                    spacing=6,
                ),
            ],
            spacing=20,
            alignment=ft.MainAxisAlignment.CENTER
        )

        return ft.Container(
            bgcolor=ft.Colors.WHITE,
            border_radius=10,
            padding=16,
            content=ft.Column(
                controls=[
                    ft.Text(
                        f"{year} – Volume de Contratos por Mês ({year})",
                        size=16,
                        weight=ft.FontWeight.W_600,
                    ),
                    legend,
                    ft.Container(
                        height=320,
                        content=bar_chart,
                    ),
                ],
                spacing=8,
                alignment=ft.MainAxisAlignment.START,
            ),
        )

    def _create_empty_state(self, message: str) -> ft.Control:
        """Mensagem simples para estados vazios."""
        return ft.Container(
            padding=20,
            content=ft.Text(message, size=14, color=ft.Colors.GREY_700),
        )

    def _create_dashboard_content(self) -> ft.Control:
        """Conteúdo padrão de visão/visão geral (cards de exemplo)."""
        return ft.Container(
            expand=True,
            content=ft.Column(
                controls=[
                    self._create_dashboard_row_1(),
                    self._create_dashboard_row_2(),
                ],
                spacing=16,
                alignment=ft.MainAxisAlignment.START,
            ),
        )

    def _create_dashboard_row_1(self) -> ft.Control:
        return ft.ResponsiveRow(
            controls=[
                self._create_card_revenue_this_month(),
                self._create_card_operational_efficiency(),
                self._create_card_client_metrics(),
            ],
            run_spacing=12,
        )

    def _create_dashboard_row_2(self) -> ft.Control:
        return ft.ResponsiveRow(
            controls=[
                self._create_card_energy_atoms(),
                self._create_card_energy_flow(),
                self._create_card_market_price(),
            ],
            run_spacing=12,
        )

    def _create_metric_card(
        self,
        title: str,
        subtitle: str,
        value: str,
        badge_text: str,
    ) -> ft.Control:
        """Cria um card de métrica individual."""
        return ft.Container(
            col=4,
            bgcolor=ft.Colors.BLUE_50,
            border_radius=10,
            padding=12,
            content=ft.Column(
                controls=[
                    ft.Text(title, size=14, weight=ft.FontWeight.W_600),
                    ft.Text(subtitle, size=12, color=ft.Colors.GREY_700),
                    ft.Row(
                        controls=[
                            ft.Text(value, size=20, weight=ft.FontWeight.BOLD),
                            ft.Container(
                                padding=ft.padding.symmetric(horizontal=6, vertical=2),
                                border_radius=20,
                                bgcolor=ft.Colors.WHITE,
                                content=ft.Text(
                                    badge_text,
                                    size=12,
                                    color=ft.Colors.GREEN_700,
                                ),
                            ),
                        ],
                        alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                    ),
                ],
                spacing=6,
                alignment=ft.MainAxisAlignment.START,
            ),
        )

    def _create_card_revenue_this_month(self) -> ft.Control:
        return self._create_metric_card(
            title="Revenue This Month",
            subtitle="Receita acumulada",
            value="R$ 1.5M",
            badge_text="+8%",
        )

    def _create_card_operational_efficiency(self) -> ft.Control:
        return self._create_metric_card(
            title="Operational Efficiency",
            subtitle="Eficiência operacional",
            value="85%",
            badge_text="Meta 80%",
        )

    def _create_card_client_metrics(self) -> ft.Control:
        return self._create_metric_card(
            title="Client Metrics",
            subtitle="Indicadores de clientes",
            value="120%",
            badge_text="Crescimento",
        )

    def _create_card_energy_atoms(self) -> ft.Control:
        return self._create_metric_card(
            title="Energy Atoms",
            subtitle="Energia contratada",
            value="2.7M",
            badge_text="Estável",
        )

    def _create_card_energy_flow(self) -> ft.Control:
        return self._create_metric_card(
            title="Energy Flow (MW)",
            subtitle="Fluxo de energia",
            value="56 MW",
            badge_text="Normal",
        )

    def _create_card_market_price(self) -> ft.Control:
        return self._create_metric_card(
            title="Market Price (R$/MWh)",
            subtitle="Preço médio",
            value="R$ 350",
            badge_text="+5%",
        )

    def _create_fluxos_content(self) -> ft.Control:
        """Conteúdo de Fluxos com muitos "gráficos" para testar o scroll.

        Cria uma grade de cards suficientemente grande para exigir
        rolagem tanto vertical quanto horizontal.
        """
        chart_rows: list[ft.Control] = []

        for row_index in range(4):
            row_controls: list[ft.Control] = []
            for col_index in range(6):
                row_controls.append(
                    self._create_fluxo_chart_card(
                        row_index=row_index,
                        col_index=col_index,
                    )
                )
            chart_rows.append(
                ft.Row(controls=row_controls, spacing=16)
            )

        return ft.Container(
            width=1600,
            height=1000,
            content=ft.Column(
                controls=chart_rows,
                spacing=16,
                alignment=ft.MainAxisAlignment.START,
            ),
        )

    def _create_contratos_content(self) -> ft.Control:
        return self._create_placeholder_section(
            "Contratos",
            "Cadastro e gestão de contratos de comercialização.",
        )

    def _create_clientes_content(self) -> ft.Control:
        return self._create_placeholder_section(
            "Clientes",
            "Lista e detalhes dos clientes atendidos.",
        )

    def _create_produtos_content(self) -> ft.Control:
        return self._create_placeholder_section(
            "Produtos",
            "Catálogo de produtos e estruturas comerciais.",
        )

    def _create_fluxo_chart_card(
        self,
        row_index: int,
        col_index: int,
    ) -> ft.Control:
        """Cria um card de "gráfico" para a seção Fluxos.

        O objetivo aqui é ocupar bastante área de tela para validar o
        comportamento de scroll horizontal e vertical.
        """
        title = f"Fluxo {row_index + 1}-{col_index + 1}"

        return ft.Container(
            width=220,
            height=160,
            bgcolor=ft.Colors.BLUE_50,
            border_radius=10,
            padding=10,
            content=ft.Column(
                controls=[
                    ft.Text(title, size=13, weight=ft.FontWeight.W_600),
                    ft.Text(
                        "Gráfico de exemplo",
                        size=11,
                        color=ft.Colors.GREY_700,
                    ),
                    ft.Container(
                        expand=True,
                        bgcolor=ft.Colors.WHITE,
                        border_radius=6,
                        alignment=ft.alignment.center,
                        content=ft.Icon(
                            name=ft.Icons.SHOW_CHART,
                            color=ft.Colors.BLUE_400,
                            size=32,
                        ),
                    ),
                ],
                spacing=6,
                alignment=ft.MainAxisAlignment.START,
            ),
        )

    def _create_placeholder_section(self, title: str, description: str) -> ft.Control:
        """Cria um conteúdo simples para seções ainda não detalhadas."""
        return ft.Container(
            expand=True,
            content=ft.Column(
                controls=[
                    ft.Text(title, size=18, weight=ft.FontWeight.W_600),
                    ft.Text(description, size=14, color=ft.Colors.GREY_700),
                ],
                spacing=8,
                alignment=ft.MainAxisAlignment.START,
            ),
        )

    # def _create_footer_container(self) -> ft.Control:
    #     return ft.Container(
    #         padding=10,
    #         alignment=ft.alignment.center,
    #         content=ft.Text(
    #             "Rodapé - Comercialização",
    #             size=12,
    #             color=ft.Colors.GREY,
    #         ),
    #     )

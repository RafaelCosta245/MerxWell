from typing import Any, Dict, Optional
from datetime import datetime

import flet as ft
from screens import BaseScreen
from screens import (
    comercializacao_contratos,
    comercializacao_novo_contrato,
    comercializacao_portfolio,
    comercializacao_visao_geral,
    comercializacao_fluxos,
    comercializacao_clientes,
    comercializacao_produtos,
    comercializacao_sazo,
    comercializacao_precos,
    comercializacao_novo_preco,
    comercializacao_propostas,
    comercializacao_nova_proposta,
)
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
        energy_type = params.get("energy_type")
        submarket = params.get("submarket")
        contract_type = params.get("contract_type")
        buyer_filter = params.get("buyer")
        seller_filter = params.get("seller")
        contracts_view = params.get("contracts_view")
        contract_id = params.get("contract_id")
        start_date = params.get("start_date")
        end_date = params.get("end_date")
        precos_view = params.get("precos_view")
        propostas_view = params.get("propostas_view")

        return self._create_main_content(
            selected_submenu,
            selected_client,
            energy_type,
            submarket,
            contract_type,
            buyer_filter,
            seller_filter,
            contracts_view,
            contract_id,
            start_date,
            end_date,
            precos_view,
            propostas_view,
        )

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
        energy_type: Optional[str],
        submarket: Optional[str],
        contract_type: Optional[str],
        buyer_filter: Optional[str],
        seller_filter: Optional[str],
        contracts_view: Optional[str],
        contract_id: Optional[str] = None,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
        precos_view: Optional[str] = None,
        propostas_view: Optional[str] = None,
    ) -> ft.Control:
        """Cria o layout principal com submenu à esquerda e conteúdo à direita."""
        return ft.Container(
            padding=2,
            expand=True,
            content=ft.Row(
                controls=[
                    self._create_submenu_column(selected_submenu),
                    self._create_subcontent_area(
                        selected_submenu,
                        selected_client,
                        energy_type,
                        submarket,
                        contract_type,
                        buyer_filter,
                        seller_filter,
                        contracts_view,
                        contract_id,
                        start_date,
                        end_date,
                        precos_view,
                        propostas_view,
                    ),
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
            ("Portfólio", "visao", ft.Icons.INSIGHTS),
            ("Visão Geral", "visao_geral", ft.Icons.DASHBOARD),
            ("Fluxos", "fluxos", ft.Icons.TIMELINE),
            ("Contratos", "contratos", ft.Icons.DESCRIPTION),
            ("Preços", "precos", ft.Icons.ATTACH_MONEY),
            ("Propostas", "propostas", ft.Icons.SHOPPING_BAG),
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
        energy_type: Optional[str],
        submarket: Optional[str],
        contract_type: Optional[str],
        buyer_filter: Optional[str],
        seller_filter: Optional[str],
        contracts_view: Optional[str],
        contract_id: Optional[str] = None,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
        precos_view: Optional[str] = None,
        propostas_view: Optional[str] = None,
    ) -> ft.Control:
        """Seleciona o conteúdo de acordo com o submenu escolhido."""
        print(
            "[ComercializacaoScreen] _create_subcontent_area",
            {
                "selected_submenu": selected_submenu,
                "contracts_view": contracts_view,
                "precos_view": precos_view,
                "propostas_view": propostas_view,
            },
        )
        if selected_submenu == "visao":
            inner = comercializacao_portfolio.create_portfolio_content(
                self,
                selected_client,
                energy_type,
                submarket,
                contract_type,
            )
        elif selected_submenu == "visao_geral":
            inner = comercializacao_visao_geral.create_visao_geral_content(self)
        elif selected_submenu == "fluxos":
            inner = comercializacao_fluxos.create_fluxos_content(self)
        elif selected_submenu == "contratos":
            if contracts_view == "new":
                print("[ComercializacaoScreen] Abrindo formulário de novo contrato")
                inner = comercializacao_novo_contrato.create_novo_contrato_content(
                    self,
                    buyer_filter,
                    seller_filter,
                    contract_id=contract_id,
                )
                # Para isolar o problema de tela em branco, retornamos o
                # formulário diretamente, sem envolver no wrapper de scroll.
                return inner

            elif contracts_view == "sazo":
                print("[ComercializacaoScreen] Abrindo formulário de sazonalidade")
                inner = comercializacao_sazo.create_sazo_content(
                    self,
                    contract_id=contract_id,
                    start_date=start_date,
                    end_date=end_date,
                )
                return inner
            else:
                print("[ComercializacaoScreen] Abrindo listagem de contratos")
                inner = comercializacao_contratos.create_contratos_content(
                    self,
                    buyer_filter,
                    seller_filter,
                )
        elif selected_submenu == "precos":
            if precos_view == "new":
                print("[ComercializacaoScreen] Abrindo formulário de novo preço")
                inner = comercializacao_novo_preco.create_novo_preco_content(self)
                return inner
            else:
                inner = comercializacao_precos.create_precos_content(self)
        elif selected_submenu == "propostas":
            if propostas_view == "new":
                print("[ComercializacaoScreen] Abrindo formulário de nova proposta")
                inner = comercializacao_nova_proposta.create_nova_proposta_content(self)
                return inner
            else:
                inner = comercializacao_propostas.create_propostas_content(self)
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
    def _create_visao_dashboard(
        self,
        selected_client: Optional[str],
        energy_type: Optional[str],
        submarket: Optional[str],
        contract_type: Optional[str],
    ) -> ft.Control:
        """Cria o dashboard de contratos por cliente.

        Exibe um filtro de cliente, métricas agregadas e gráficos por ano
        com volumes de compra e venda por mês.
        """
        clients = list_contract_clients()

        client_value = selected_client if selected_client in clients else None

        filters_row, current_filters = self._create_filters_row(
            clients,
            client_value,
            energy_type,
            submarket,
            contract_type,
        )

        if client_value:
            data = get_client_dashboard_data(
                client_value,
                energy_type=current_filters["energy_type"],
                submarket=current_filters["submarket"],
                contract_type=current_filters["contract_type"],
            )
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
                    filters_row,
                    metrics_row,
                    charts,
                ],
                spacing=20,
                alignment=ft.MainAxisAlignment.START,
            ),
        )

    def _create_filters_row(
        self,
        clients: list[str],
        selected_client: Optional[str],
        energy_type: Optional[str],
        submarket: Optional[str],
        contract_type: Optional[str],
    ) -> tuple[ft.Control, Dict[str, Optional[str]]]:
        """Cria a linha de filtros (cliente + tipo de energia + submercado + modalidade)."""

        dropdown_width = 220

        # Restringe clientes a uma lista fixa, mas apenas para aqueles que
        # existem na base retornada por list_contract_clients().
        allowed_clients = {"NOVO COM", "MERX", "FORTLEV SOLAR"}
        client_options_list = [c for c in clients if c in allowed_clients]

        client_dd = ft.Dropdown(
            label="Cliente",
            hint_text="Escolha um cliente...",
            options=[ft.dropdown.Option(c) for c in client_options_list],
            value=selected_client if selected_client in client_options_list else None,
            width=dropdown_width,
        )

        energy_dd = ft.Dropdown(
            label="Tipo de Energia",
            hint_text="Todos",
            options=[
                ft.dropdown.Option("I5"),
                ft.dropdown.Option("I1"),
                ft.dropdown.Option("I0"),
                ft.dropdown.Option("CONV"),
                ft.dropdown.Option("CQ5"),
            ],
            value=energy_type,
            width=dropdown_width,
        )

        submarket_dd = ft.Dropdown(
            label="Submercado",
            hint_text="Todos",
            options=[
                ft.dropdown.Option("SE/CO"),
                ft.dropdown.Option("NE"),
                ft.dropdown.Option("N"),
                ft.dropdown.Option("S"),
            ],
            value=submarket,
            width=dropdown_width,
        )

        contract_type_dd = ft.Dropdown(
            label="Modalidade",
            hint_text="Todas",
            options=[
                ft.dropdown.Option("ATACADISTA"),
                ft.dropdown.Option("VAREJISTA"),
                ft.dropdown.Option("AUTOPRODUÇÃO"),
            ],
            value=contract_type,
            width=dropdown_width,
        )

        def apply_filters(_: ft.ControlEvent) -> None:
            self.navigation.go(
                "/comercializacao",
                params={
                    "submenu": "visao",
                    "client": client_dd.value,
                    "energy_type": energy_dd.value,
                    "submarket": submarket_dd.value,
                    "contract_type": contract_type_dd.value,
                },
            )

        client_dd.on_change = apply_filters
        energy_dd.on_change = apply_filters
        submarket_dd.on_change = apply_filters
        contract_type_dd.on_change = apply_filters

        row = ft.Row(
            controls=[client_dd, energy_dd, submarket_dd, contract_type_dd],
            spacing=16,
            alignment=ft.MainAxisAlignment.START,
        )

        current_filters = {
            "energy_type": energy_type,
            "submarket": submarket,
            "contract_type": contract_type,
        }

        return row, current_filters

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
        buy_mwh = list(year_data.get("buy", []))
        sell_mwh = list(year_data.get("sell", []))

        # Garante que as listas tenham pelo menos o tamanho de months
        while len(buy_mwh) < len(months):
            buy_mwh.append(0.0)
        while len(sell_mwh) < len(months):
            sell_mwh.append(0.0)

        # Horas por mês para converter MWh -> MWm
        hours_per_month = [
            744.0,  # Jan
            672.0,  # Fev
            744.0,  # Mar
            720.0,  # Abr
            744.0,  # Mai
            720.0,  # Jun
            744.0,  # Jul
            744.0,  # Ago
            720.0,  # Set
            744.0,  # Out
            720.0,  # Nov
            744.0,  # Dez
        ]

        buy_mwm: list[float] = []
        sell_mwm: list[float] = []
        diff_mwm: list[float] = []

        for i in range(len(months)):
            hours = hours_per_month[i] if i < len(hours_per_month) else 744.0
            b = float(buy_mwh[i] or 0.0) / hours if hours > 0 else 0.0
            s = float(sell_mwh[i] or 0.0) / hours if hours > 0 else 0.0
            d = b - s
            buy_mwm.append(b)
            sell_mwm.append(s)
            diff_mwm.append(d)

        max_volume = max(
            max((abs(v) for v in buy_mwm), default=0.0),
            max((abs(v) for v in sell_mwm), default=0.0),
            max((abs(v) for v in diff_mwm), default=0.0),
        ) or 1.0
        max_y = max_volume * 1.2

        print(
            "[ComercializacaoScreen] Ano (MWm)",
            year,
            {
                "buy_mwm": buy_mwm,
                "sell_mwm": sell_mwm,
                "diff_mwm": diff_mwm,
            },
        )

        buy_avg_price = float(year_data.get("buy_avg_price", 0.0) or 0.0)
        sell_avg_price = float(year_data.get("sell_avg_price", 0.0) or 0.0)

        bar_groups: list[ft.BarChartGroup] = []
        for i, label in enumerate(months):
            diff_value = diff_mwm[i]
            diff_color = (
                ft.Colors.RED_400 if diff_value < 0 else ft.Colors.AMBER_400
            )
            if diff_value > 0:
                diff_label = "Sobra"
            elif diff_value < 0:
                diff_label = "Déficit"
            else:
                diff_label = "Diferença"
            bar_groups.append(
                ft.BarChartGroup(
                    x=i,
                    bar_rods=[
                        ft.BarChartRod(
                            from_y=0,
                            to_y=buy_mwm[i],
                            width=10,
                            color=ft.Colors.GREEN_400,
                            tooltip=f"Compra: {buy_mwm[i]:.2f} MWm",
                            border_radius=4,
                        ),
                        ft.BarChartRod(
                            from_y=0,
                            to_y=sell_mwm[i],
                            width=10,
                            color=ft.Colors.BLUE_400,
                            tooltip=f"Venda: {sell_mwm[i]:.2f} MWm",
                            border_radius=4,
                        ),
                        ft.BarChartRod(
                            from_y=0,
                            to_y=abs(diff_value),
                            width=10,
                            color=diff_color,
                            tooltip=f"{diff_label} - {diff_value:.2f} MWm",
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
                title=ft.Text("Volume (MWm)", size=12, weight=ft.FontWeight.BOLD),
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
        def _format_price(label: str, value: float) -> str:
            if value <= 0:
                return f"{label} - Preço médio: N/A"
            return f"{label} - Preço médio: R$ {value:.2f}/MWh"

        # Determina comportamento médio da diferença para legenda
        has_positive_diff = any(d > 0 for d in diff_mwm)
        has_negative_diff = any(d < 0 for d in diff_mwm)

        diff_legend_items: list[ft.Control] = []
        if has_positive_diff:
            diff_legend_items.append(
                ft.Row(
                    controls=[
                        ft.Container(
                            width=16,
                            height=16,
                            bgcolor=ft.Colors.AMBER_400,
                            border_radius=4,
                        ),
                        ft.Text("Sobra", size=11, color=ft.Colors.GREY_700),
                    ],
                    spacing=6,
                )
            )
        if has_negative_diff:
            diff_legend_items.append(
                ft.Row(
                    controls=[
                        ft.Container(
                            width=16,
                            height=16,
                            bgcolor=ft.Colors.RED_400,
                            border_radius=4,
                        ),
                        ft.Text("Déficit", size=11, color=ft.Colors.GREY_700),
                    ],
                    spacing=6,
                )
            )

        legend_controls: list[ft.Control] = [
            ft.Row(
                controls=[
                    ft.Container(
                        width=16,
                        height=16,
                        bgcolor=ft.Colors.GREEN_400,
                        border_radius=4,
                    ),
                    ft.Text(
                        _format_price("Compra", buy_avg_price),
                        size=11,
                        color=ft.Colors.GREY_700,
                    ),
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
                    ft.Text(
                        _format_price("Venda", sell_avg_price),
                        size=11,
                        color=ft.Colors.GREY_700,
                    ),
                ],
                spacing=6,
            ),
        ]

        legend_controls.extend(diff_legend_items)

        legend = ft.Row(
            controls=legend_controls,
            spacing=20,
            alignment=ft.MainAxisAlignment.CENTER,
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

    # ------------------------------------------------------------------
    # Helpers para tabela de contratos
    # ------------------------------------------------------------------

    def _format_date(self, value: Any) -> str:
        """Formata datas ISO/DateTime como dd/mm/aaaa."""
        if value is None:
            return "-"
        s = str(value)
        if not s:
            return "-"
        try:
            # Tenta parse ISO completo
            dt = datetime.fromisoformat(s.replace("Z", "+00:00"))
            return dt.strftime("%d/%m/%Y")
        except Exception:
            # Fallback em caso de formato inesperado
            if len(s) >= 10:
                return f"{s[8:10]}/{s[5:7]}/{s[0:4]}"
            return s

    def _create_contracts_table(self, contracts: list[Dict[str, Any]]) -> ft.Control:
        headers = [
            "Cód. Contrato",
            "Comprador",
            "Vendedor",
            "Energia",
            "Início",
            "Fim",
            "Editar",
            "Sazo",
            "Excluir",
        ]

        widths = [130, 220, 220, 110, 110, 110, 80, 80, 80]

        def header_cell(text: str, width: int) -> ft.Control:
            return ft.Container(
                content=ft.Text(
                    text,
                    size=13,
                    weight=ft.FontWeight.BOLD,
                    color=ft.Colors.WHITE,
                    text_align=ft.TextAlign.CENTER,
                ),
                width=width,
                height=44,
                bgcolor=ft.Colors.BLUE_700,
                padding=10,
                alignment=ft.alignment.center,
                border=ft.border.all(1, ft.Colors.BLUE_900),
            )

        def data_cell(text: str, width: int, row_index: int) -> ft.Control:
            bg_color = ft.Colors.WHITE if row_index % 2 == 0 else ft.Colors.GREY_50
            return ft.Container(
                content=ft.Text(
                    text,
                    size=12,
                    color=ft.Colors.GREY_900,
                    text_align=ft.TextAlign.CENTER,
                ),
                width=width,
                height=40,
                bgcolor=bg_color,
                padding=10,
                alignment=ft.alignment.center,
                border=ft.border.all(1, ft.Colors.GREY_300),
            )

        def action_button(
            icon: str,
            tooltip: str,
            width: int,
            row_index: int,
            on_click,
        ) -> ft.Control:
            bg_color = ft.Colors.WHITE if row_index % 2 == 0 else ft.Colors.GREY_50
            return ft.Container(
                content=ft.IconButton(
                    icon=icon,
                    icon_color=ft.Colors.BLACK,
                    tooltip=tooltip,
                    on_click=on_click,
                ),
                width=width,
                height=40,
                bgcolor=bg_color,
                alignment=ft.alignment.center,
                border=ft.border.all(1, ft.Colors.GREY_300),
            )

        header_row = ft.Row(
            controls=[header_cell(headers[i], widths[i]) for i in range(len(headers))],
            spacing=0,
        )

        data_rows: list[ft.Control] = []
        for idx, c in enumerate(contracts):
            code = str(c.get("contract_code") or "-")
            contractor = str(c.get("contractor") or "-")
            seller = str(c.get("service_provider") or "-")
            energy = str(c.get("energy_source_type") or "-")
            start = self._format_date(c.get("contract_start_date"))
            end = self._format_date(c.get("contract_end_date"))

            def make_on_click(action: str, contract_code: str):
                return lambda _: print(f"Ação {action} para contrato {contract_code}")

            row = ft.Row(
                controls=[
                    data_cell(code, widths[0], idx),
                    data_cell(contractor, widths[1], idx),
                    data_cell(seller, widths[2], idx),
                    data_cell(energy, widths[3], idx),
                    data_cell(start, widths[4], idx),
                    data_cell(end, widths[5], idx),
                    action_button(
                        ft.Icons.EDIT,
                        "Editar contrato",
                        widths[6],
                        idx,
                        make_on_click("editar", code),
                    ),
                    action_button(
                        ft.Icons.CALENDAR_MONTH,
                        "Editar sazonalidade",
                        widths[7],
                        idx,
                        make_on_click("sazonalidade", code),
                    ),
                    action_button(
                        ft.Icons.DELETE,
                        "Excluir contrato",
                        widths[8],
                        idx,
                        make_on_click("excluir", code),
                    ),
                ],
                spacing=0,
            )
            data_rows.append(row)

        total_width = sum(widths)

        table_column = ft.Column(
            controls=[header_row] + data_rows,
            spacing=0,
            scroll=ft.ScrollMode.AUTO,
        )

        return ft.Container(
            content=table_column,
            width=total_width,
            border=ft.border.all(1, ft.Colors.GREY_300),
            border_radius=8,
            bgcolor=ft.Colors.WHITE,
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

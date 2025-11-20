from typing import Any
import flet as ft

def create_precos_content(screen: Any) -> ft.Control:
    """
    Cria o conteúdo da tela de Preços (antigo Clientes), com estrutura de dashboard.
    """
    
    # --- 1. Cabeçalho (Título e Subtítulo) ---
    header = ft.Column(
        controls=[
            ft.Text("Preços", size=24, weight=ft.FontWeight.BOLD, color=ft.Colors.BLACK87),
            ft.Text("Gestão de preços de mercado e curvas futuras.", size=14, color=ft.Colors.GREY_600),
        ],
        spacing=4,
    )

    # --- 2. Cards de Ação (Topo) ---
    # Exemplo da imagem: "Novo Contrato", "Buscar Contrato", "Meus Contratos", "Configurações"
    # Adaptando para contexto de Preços, mas mantendo estrutura visual.
    
    def action_card(icon: str, title: str, subtitle: str = "", on_click=None) -> ft.Control:
        return ft.Container(
            content=ft.Row(
                controls=[
                    ft.Icon(icon, size=32, color=ft.Colors.BLUE_600),
                    ft.Column(
                        controls=[
                            ft.Text(title, weight=ft.FontWeight.BOLD, size=16, color=ft.Colors.BLUE_900),
                            ft.Text(subtitle, size=12, color=ft.Colors.GREY_600) if subtitle else ft.Container(),
                        ],
                        spacing=2,
                        alignment=ft.MainAxisAlignment.CENTER,
                    ),
                ],
                alignment=ft.MainAxisAlignment.CENTER,
                spacing=15,
            ),
            width=240,
            height=80,
            bgcolor=ft.Colors.WHITE,
            border=ft.border.all(1, ft.Colors.BLUE_100),
            border_radius=12,
            padding=15,
            # Sombra suave
            shadow=ft.BoxShadow(
                spread_radius=1,
                blur_radius=5,
                color=ft.Colors.BLUE_50,
                offset=ft.Offset(0, 2),
            ),
            on_click=on_click,
            ink=True if on_click else False,  # Efeito de clique
        )

    # Função para navegar para o formulário de novo preço
    def go_to_novo_preco(e):
        screen.navigation.go(
            "/comercializacao",
            params={
                "submenu": "precos",
                "precos_view": "new",
            },
        )

    cards_row = ft.Row(
        controls=[
            action_card(ft.Icons.ADD_CIRCLE_OUTLINE, "Novo Preço", "Cadastrar curva", on_click=go_to_novo_preco),
            action_card(ft.Icons.SEARCH, "Buscar Preço", "Consultar histórico"),
            action_card(ft.Icons.LIST_ALT, "Meus Preços", "Gerenciar cadastros"),
            action_card(ft.Icons.SETTINGS, "Configurações", "Parâmetros gerais"),
        ],
        spacing=20,
        alignment=ft.MainAxisAlignment.START,
    )

    # --- 3. Botões de Filtro/Exportação ---
    def action_button(text: str) -> ft.Control:
        return ft.ElevatedButton(
            text=text,
            bgcolor=ft.Colors.BLUE_700,
            color=ft.Colors.WHITE,
            style=ft.ButtonStyle(
                shape=ft.RoundedRectangleBorder(radius=8),
                padding=ft.padding.symmetric(horizontal=20, vertical=18),
            ),
        )

    buttons_row = ft.Row(
        controls=[
            action_button("Adicionar Filtro"),
            action_button("Exportar Dados"),
        ],
        spacing=15,
        alignment=ft.MainAxisAlignment.START,
    )

    # --- 4. Seção de Gráficos (Preços Médios) ---
    # Placeholder para os gráficos. Em uma implementação real, usaríamos ft.LineChart.
    # Aqui vamos simular o visual com containers.

    def chart_placeholder(title: str) -> ft.Control:
        return ft.Container(
            content=ft.Column(
                controls=[
                    ft.Text(title, size=14, weight=ft.FontWeight.W_600, color=ft.Colors.GREY_800),
                    ft.Container(
                        content=ft.Text("Gráfico aqui", color=ft.Colors.GREY_400),
                        alignment=ft.alignment.center,
                        bgcolor=ft.Colors.BLUE_50,
                        border_radius=8,
                        expand=True,
                    )
                ],
                spacing=10,
                expand=True,
            ),
            expand=True,
            height=250,
            padding=10,
        )

    charts_section = ft.Container(
        content=ft.Column(
            controls=[
                ft.Text("Preços Médios de Energia", size=18, weight=ft.FontWeight.BOLD, color=ft.Colors.BLACK87),
                ft.Row(
                    controls=[
                        chart_placeholder("Preço PLD - Últimos 12 Meses"),
                        chart_placeholder("Preço CCEAL - Último Ano"),
                    ],
                    spacing=20,
                    expand=True,
                ),
            ],
            spacing=20,
            expand=True,
        ),
        bgcolor=ft.Colors.WHITE,
        border_radius=12,
        padding=25,
        shadow=ft.BoxShadow(
            spread_radius=1,
            blur_radius=10,
            color=ft.Colors.GREY_100,
            offset=ft.Offset(0, 4),
        ),
        height=400, # Altura fixa para o container de gráficos
    )

    # --- Montagem Final ---
    content = ft.Column(
        controls=[
            # header,
            # ft.Container(height=10), # Espaçamento
            cards_row,
            ft.Container(height=5),
            buttons_row,
            ft.Container(height=5),
            charts_section,
        ],
        spacing=20,
        scroll=ft.ScrollMode.AUTO,
        expand=True,
    )

    return ft.Container(
        content=content,
        padding=30,
        expand=True,
        bgcolor=ft.Colors.GREY_50, # Fundo levemente cinza para destacar os cards brancos
    )

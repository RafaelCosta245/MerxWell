from typing import Any, Dict, Optional
import flet as ft

def create_novo_preco_content(screen: Any) -> ft.Control:
    """
    Formulário de cadastro de preços com abas por ano (2026-2035).
    Cada aba contém uma tabela de preços por submercado e tipo de energia.
    """
    
    # Anos das abas
    anos = list(range(2026, 2036))  # 2026 a 2035
    
    # Submercados e tipos de energia
    submercados = ["SE/CO", "S", "NE", "N"]
    tipos_energia = ["CONV", "I5", "I1", "CQ5"]
    
    # Armazenar dados do formulário
    # Estrutura: { ano: { (submercado, tipo_energia): valor } }
    form_data = {}
    
    def criar_campo_preco(ano: int, submercado: str, tipo_energia: str, width=100) -> ft.TextField:
        """Cria um campo de texto para entrada de preço."""
        def on_change(e):
            if ano not in form_data:
                form_data[ano] = {}
            
            valor = e.control.value
            try:
                # Substitui vírgula por ponto
                val_str = str(valor).replace(',', '.')
                val_float = float(val_str) if val_str else None
                form_data[ano][(submercado, tipo_energia)] = val_float
            except ValueError:
                form_data[ano][(submercado, tipo_energia)] = None
        
        return ft.TextField(
            value="",
            text_align=ft.TextAlign.CENTER,
            border_color=ft.Colors.GREY_400,
            focused_border_color=ft.Colors.BLUE_600,
            color=ft.Colors.BLACK,
            width=width,
            height=40,
            text_size=12,
            content_padding=10,
            on_change=on_change,
        )
    
    def criar_tabela_ano(ano: int) -> ft.Control:
        """Cria a tabela de preços para um ano específico."""
        
        # Cabeçalho da tabela
        header_cells = [
            ft.Container(
                content=ft.Text("Submercado", size=12, weight=ft.FontWeight.BOLD, color=ft.Colors.WHITE),
                bgcolor=ft.Colors.BLUE_700,
                padding=10,
                width=120,
                height=44,
                alignment=ft.alignment.center,
                border=ft.border.all(1, ft.Colors.BLUE_900),
            )
        ]
        
        for tipo in tipos_energia:
            header_cells.append(
                ft.Container(
                    content=ft.Text(tipo, size=12, weight=ft.FontWeight.BOLD, color=ft.Colors.WHITE),
                    bgcolor=ft.Colors.BLUE_700,
                    padding=10,
                    width=100,
                    height=44,
                    alignment=ft.alignment.center,
                    border=ft.border.all(1, ft.Colors.BLUE_900),
                )
            )
        
        header_row = ft.Row(controls=header_cells, spacing=0)
        
        # Linhas de dados
        data_rows = []
        for idx, submercado in enumerate(submercados):
            bg_color = ft.Colors.WHITE if idx % 2 == 0 else ft.Colors.GREY_50
            
            row_cells = [
                ft.Container(
                    content=ft.Text(submercado, size=12, color=ft.Colors.GREY_900, text_align=ft.TextAlign.CENTER),
                    bgcolor=bg_color,
                    padding=10,
                    width=120,
                    height=40,
                    alignment=ft.alignment.center,
                    border=ft.border.all(1, ft.Colors.GREY_300),
                )
            ]
            
            for tipo in tipos_energia:
                campo = criar_campo_preco(ano, submercado, tipo)
                row_cells.append(
                    ft.Container(
                        content=campo,
                        bgcolor=bg_color,
                        width=100,
                        height=40,
                        alignment=ft.alignment.center,
                        border=ft.border.all(1, ft.Colors.GREY_300),
                    )
                )
            
            data_rows.append(ft.Row(controls=row_cells, spacing=0))
        
        # Tabela completa
        table = ft.Column(
            controls=[header_row] + data_rows,
            spacing=0,
        )
        
        # Container com scroll
        return ft.Container(
            content=ft.Row(
                controls=[table],
                scroll=ft.ScrollMode.ALWAYS,
            ),
            padding=20,
        )
    
    # Criar abas para cada ano
    tabs_list = []
    for ano in anos:
        tab_content = criar_tabela_ano(ano)
        tabs_list.append(
            ft.Tab(
                text=str(ano),
                content=tab_content,
            )
        )
    
    tabs = ft.Tabs(
        selected_index=0,
        animation_duration=300,
        tabs=tabs_list,
        expand=1,
    )
    
    # Funções dos botões
    def on_save(e):
        print("Salvando dados de preços...")
        print(form_data)
        # TODO: Implementar salvamento no banco de dados
        
        snackbar = ft.SnackBar(
            content=ft.Text("Preços salvos com sucesso!"),
            bgcolor=ft.Colors.GREEN_600,
        )
        screen.page.overlay.append(snackbar)
        snackbar.open = True
        screen.page.update()
    
    def on_cancel(e):
        print("Cancelando cadastro de preços...")
        screen.navigation.go(
            "/comercializacao",
            params={"submenu": "precos"},
        )
    
    def on_forward_srn(e):
        print("Forward SRN clicado...")
        # TODO: Implementar lógica do Forward SRN
        
        snackbar = ft.SnackBar(
            content=ft.Text("Função Forward SRN será implementada"),
            bgcolor=ft.Colors.BLUE_600,
        )
        screen.page.overlay.append(snackbar)
        snackbar.open = True
        screen.page.update()
    
    # Botões de ação
    button_width = 160
    button_height = 42
    
    actions_row = ft.Row(
        controls=[
            ft.ElevatedButton(
                text="Cancelar",
                icon=ft.Icons.CANCEL,
                bgcolor=ft.Colors.GREY_400,
                color=ft.Colors.WHITE,
                width=button_width,
                height=button_height,
                on_click=on_cancel,
            ),
            ft.ElevatedButton(
                text="Forward SRN",
                icon=ft.Icons.TRENDING_UP,
                bgcolor=ft.Colors.BLUE_600,
                color=ft.Colors.WHITE,
                width=button_width,
                height=button_height,
                on_click=on_forward_srn,
            ),
            ft.ElevatedButton(
                text="Salvar",
                icon=ft.Icons.CHECK_CIRCLE,
                bgcolor=ft.Colors.GREEN_600,
                color=ft.Colors.WHITE,
                width=button_width,
                height=button_height,
                on_click=on_save,
            ),
        ],
        spacing=12,
        alignment=ft.MainAxisAlignment.END,
    )
    
    # Card principal
    card = ft.Container(
        bgcolor=ft.Colors.WHITE,
        border_radius=10,
        padding=20,
        border=ft.border.all(1, ft.Colors.BLUE_100),
        content=ft.Column(
            controls=[
                ft.Text(
                    "Cadastro de Preços",
                    size=18,
                    weight=ft.FontWeight.W_600,
                ),
                ft.Container(height=8),
                tabs,
                ft.Container(height=12),
                actions_row,
            ],
            spacing=8,
            alignment=ft.MainAxisAlignment.START,
        ),
    )
    
    return ft.Container(
        expand=True,
        padding=20,
        bgcolor=ft.Colors.BLUE_50,
        content=card,
    )

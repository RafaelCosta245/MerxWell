from typing import Any, Dict, Optional, List
from datetime import datetime
import flet as ft

# Constantes de horas por mês (simplificado)
HOURS_PER_MONTH = [744, 672, 744, 720, 744, 720, 744, 744, 720, 744, 720, 744]
MESES_KEYS = ["january", "february", "march", "april", "may", "june", "july", "august", "september", "october", "november", "december"]
MESES_LABELS = ["Jan", "Fev", "Mar", "Abr", "Mai", "Jun", "Jul", "Ago", "Set", "Out", "Nov", "Dez"]

def create_nova_proposta_content(screen: Any) -> ft.Control:
    """
    Formulário de Nova Proposta com 3 abas:
    1. Dados Gerais
    2. Cond. Comerciais (Tabela dinâmica por ano)
    3. Dados Complementares
    """

    # --- Estado do Formulário ---
    form_data = {
        "cnpj": "",
        "razao_social": "",
        "submercado": None,
        "inicio_suprimento": "",
        "fim_suprimento": "",
        "tipo_energia": None,
        "modulacao": None,
        "data_faturamento": "",
        "garantia": None,
        "qty_meses": "",
        "data_base": "",
        "validade_proposta": "",
        "commercial_conditions": {} # {year: {price, flex, sazo, vol, ...}}
    }
    
    # Referências para a tabela comercial
    commercial_table_ref = ft.Ref[ft.Column]()
    commercial_rows_refs = [] # Lista de dicts com refs dos campos da tabela

    # --- Helpers de Data ---
    def _get_years_range(start_str: str, end_str: str) -> List[int]:
        print(f"[DEBUG] _get_years_range inputs: start='{start_str}', end='{end_str}'")
        try:
            dt_start = datetime.strptime(start_str.strip(), "%d/%m/%Y")
            dt_end = datetime.strptime(end_str.strip(), "%d/%m/%Y")
            if dt_start > dt_end:
                print("[DEBUG] Start date > End date")
                return []
            years = list(range(dt_start.year, dt_end.year + 1))
            print(f"[DEBUG] Years generated: {years}")
            return years
        except ValueError as e:
            print(f"[DEBUG] Date parsing error: {e}")
            return []

    # --- Aba 1: Dados Gerais ---
    cnpj_field = ft.TextField(label="CNPJ", width=300)
    razao_social_field = ft.TextField(label="Razão Social", width=500)
    submercado_dd = ft.Dropdown(
        label="Submercado",
        width=300,
        options=[
            ft.dropdown.Option("SE/CO"),
            ft.dropdown.Option("NE"),
            ft.dropdown.Option("N"),
            ft.dropdown.Option("S"),
        ]
    )
    inicio_suprimento_field = ft.TextField(
        label="Início Suprimento (dd/mm/aaaa)", 
        width=240,
        hint_text="01/01/2026"
    )
    fim_suprimento_field = ft.TextField(
        label="Fim Suprimento (dd/mm/aaaa)", 
        width=240,
        hint_text="31/12/2030"
    )
    tipo_energia_dd = ft.Dropdown(
        label="Tipo de Energia",
        width=300,
        options=[
            ft.dropdown.Option("I5"),
            ft.dropdown.Option("I1"),
            ft.dropdown.Option("I0"),
            ft.dropdown.Option("CONV"),
            ft.dropdown.Option("CQ5"),
        ]
    )

    dados_gerais_tab = ft.Container(
        padding=20,
        content=ft.Column(
            controls=[
                ft.Row([cnpj_field, razao_social_field]),
                ft.Row([submercado_dd, tipo_energia_dd]),
                ft.Row([inicio_suprimento_field, fim_suprimento_field]),
            ],
            spacing=20
        )
    )

    # --- Aba 2: Condições Comerciais (Lógica Dinâmica) ---
    
    def criar_campo_tabela(width=80, value=None, on_change=None):
        return ft.TextField(
            value=str(value) if value is not None else "",
            text_align=ft.TextAlign.CENTER,
            width=width,
            height=40,
            text_size=12,
            content_padding=10,
            on_change=on_change,
            border_color=ft.Colors.GREY_400,
        )

    def atualizar_dados_comerciais(ano, campo, valor):
        if ano not in form_data["commercial_conditions"]:
            form_data["commercial_conditions"][ano] = {}
        
        # Tratamento numérico básico
        try:
            if campo in ["price", "flex", "sazo", "volume"] or campo in MESES_KEYS:
                val_str = str(valor).replace(',', '.')
                val_float = float(val_str) if val_str else None
                form_data["commercial_conditions"][ano][campo] = val_float
                
                # Lógica Flat
                if campo == "volume":
                    row_ref = next((r for r in commercial_rows_refs if r['ano'] == ano), None)
                    if row_ref and row_ref['flat'].value:
                         aplicar_flat(ano, row_ref, val_float)
            else:
                form_data["commercial_conditions"][ano][campo] = valor
        except ValueError:
             form_data["commercial_conditions"][ano][campo] = None

    def aplicar_flat(ano, row_ref, vol_medio):
        if vol_medio is None:
            return
        for idx, mes_key in enumerate(MESES_KEYS):
            horas = HOURS_PER_MONTH[idx]
            valor_mes = vol_medio * horas
            form_data["commercial_conditions"][ano][mes_key] = valor_mes
            if idx < len(row_ref['meses']):
                row_ref['meses'][idx].value = f"{valor_mes:.2f}"
        screen.page.update()

    def on_flat_change(e, ano):
        is_flat = e.control.value
        if is_flat:
            vol_medio = form_data["commercial_conditions"].get(ano, {}).get("volume")
            row_ref = next((r for r in commercial_rows_refs if r['ano'] == ano), None)
            if row_ref:
                aplicar_flat(ano, row_ref, vol_medio)

    def copiar_primeira_linha(e):
        if len(commercial_rows_refs) < 2:
            return
        
        first_row = commercial_rows_refs[0]
        ano_origem = first_row['ano']
        dados_origem = form_data["commercial_conditions"].get(ano_origem, {})

        for i in range(1, len(commercial_rows_refs)):
            row = commercial_rows_refs[i]
            ano_destino = row['ano']
            
            # Copiar UI
            row['preco'].value = first_row['preco'].value
            row['flex'].value = first_row['flex'].value
            row['sazo'].value = first_row['sazo'].value
            row['volume'].value = first_row['volume'].value
            
            for j in range(12):
                row['meses'][j].value = first_row['meses'][j].value
            
            # Copiar Dados
            if ano_destino not in form_data["commercial_conditions"]:
                form_data["commercial_conditions"][ano_destino] = {}
            
            for k, v in dados_origem.items():
                form_data["commercial_conditions"][ano_destino][k] = v
        
        screen.page.update()
        screen.page.show_snack_bar(ft.SnackBar(ft.Text("Dados replicados com sucesso!"), bgcolor=ft.Colors.GREEN_600))

    def gerar_tabela_comercial():
        commercial_rows_refs.clear()
        years = _get_years_range(inicio_suprimento_field.value, fim_suprimento_field.value)
        
        if not years:
            return ft.Text("Preencha o período de suprimento corretamente na aba 'Dados Gerais'.", color=ft.Colors.RED_500)

        # Cabeçalho
        header = ft.Row(
            controls=[
                ft.Container(width=40), # Copy btn space
                ft.Container(ft.Text("Ano", weight=ft.FontWeight.BOLD, size=12), width=50, alignment=ft.alignment.center),
                ft.Container(ft.Text("Preço", weight=ft.FontWeight.BOLD, size=12), width=80, alignment=ft.alignment.center),
                ft.Container(ft.Text("Flex", weight=ft.FontWeight.BOLD, size=12), width=80, alignment=ft.alignment.center),
                ft.Container(ft.Text("Sazo", weight=ft.FontWeight.BOLD, size=12), width=80, alignment=ft.alignment.center),
                ft.Container(ft.Text("Vol", weight=ft.FontWeight.BOLD, size=12), width=80, alignment=ft.alignment.center),
                ft.Container(ft.Text("Flat", weight=ft.FontWeight.BOLD, size=12), width=50, alignment=ft.alignment.center),
            ] + [
                ft.Container(ft.Text(m, weight=ft.FontWeight.BOLD, size=12), width=70, alignment=ft.alignment.center) for m in MESES_LABELS
            ],
            spacing=5
        )

        rows_controls = [header, ft.Divider()]

        for idx, ano in enumerate(years):
            refs = {'ano': ano}
            
            # Campos
            preco = criar_campo_tabela(80, on_change=lambda e, a=ano: atualizar_dados_comerciais(a, 'price', e.control.value))
            flex = criar_campo_tabela(80, on_change=lambda e, a=ano: atualizar_dados_comerciais(a, 'flex', e.control.value))
            sazo = criar_campo_tabela(80, on_change=lambda e, a=ano: atualizar_dados_comerciais(a, 'sazo', e.control.value))
            vol = criar_campo_tabela(80, on_change=lambda e, a=ano: atualizar_dados_comerciais(a, 'volume', e.control.value))
            flat = ft.Switch(value=False, height=30, active_color=ft.Colors.ORANGE_600, on_change=lambda e, a=ano: on_flat_change(e, a))
            
            refs.update({'preco': preco, 'flex': flex, 'sazo': sazo, 'volume': vol, 'flat': flat, 'meses': []})
            
            meses_controls = []
            for mk in MESES_KEYS:
                mc = criar_campo_tabela(70, on_change=lambda e, a=ano, k=mk: atualizar_dados_comerciais(a, k, e.control.value))
                meses_controls.append(mc)
                refs['meses'].append(mc)

            # Botão Copiar (só na primeira linha)
            copy_btn = ft.IconButton(ft.Icons.CONTENT_COPY, icon_size=20, icon_color=ft.Colors.BLUE_600, on_click=copiar_primeira_linha) if idx == 0 else ft.Container(width=40)

            row = ft.Row(
                controls=[
                    ft.Container(copy_btn, width=40),
                    ft.Container(ft.Text(str(ano), size=12, weight=ft.FontWeight.BOLD), width=50, alignment=ft.alignment.center),
                    preco, flex, sazo, vol, 
                    ft.Container(flat, width=50, alignment=ft.alignment.center),
                ] + meses_controls,
                spacing=5
            )
            rows_controls.append(row)
            commercial_rows_refs.append(refs)

        return ft.Column(controls=rows_controls, spacing=5, scroll=ft.ScrollMode.ALWAYS)

    def on_tab_change(e):
        # Se mudou para a aba Comercial (index 1), regenera a tabela
        if e.control.selected_index == 1:
            content = gerar_tabela_comercial()
            # Atualiza o container da tabela
            # Precisamos de um container fixo para substituir o conteudo
            commercial_tab_content.content = content
            commercial_tab_content.update()

    commercial_tab_content = ft.Container(padding=10) # Placeholder
    
    comercial_tab = ft.Container(
        padding=20,
        content=ft.Column(
            controls=[
                ft.Text("Condições Comerciais por Ano", size=16, weight=ft.FontWeight.BOLD),
                ft.Text("Preencha o período de suprimento na aba 'Dados Gerais' para gerar as linhas.", size=12, color=ft.Colors.GREY_600),
                ft.Divider(),
                ft.Row([commercial_tab_content], scroll=ft.ScrollMode.ALWAYS, expand=True)
            ]
        )
    )

    # --- Aba 3: Dados Complementares ---
    modulacao_dd = ft.Dropdown(
        label="Modulação", width=300,
        options=[ft.dropdown.Option("FLAT"), ft.dropdown.Option("CARGA")]
    )
    data_fat_pag_field = ft.TextField(label="Data de faturamento e pagamento", width=400)
    garantia_dd = ft.Dropdown(
        label="Garantia", width=300,
        options=[ft.dropdown.Option("Seguro Garantia"), ft.dropdown.Option("Carta fiança"), ft.dropdown.Option("Todas")]
    )
    qty_meses_field = ft.TextField(label="Qty_meses", width=200)
    data_base_field = ft.TextField(label="Data Base", width=200)
    validade_proposta_field = ft.TextField(label="Validade da proposta", width=200)

    complementares_tab = ft.Container(
        padding=20,
        content=ft.Column(
            controls=[
                ft.Row([modulacao_dd, garantia_dd]),
                ft.Row([data_fat_pag_field, qty_meses_field]),
                ft.Row([data_base_field, validade_proposta_field]),
            ],
            spacing=20
        )
    )

    # --- Tabs Control ---
    tabs = ft.Tabs(
        selected_index=0,
        animation_duration=300,
        on_change=on_tab_change,
        tabs=[
            ft.Tab(text="Dados Gerais", content=dados_gerais_tab),
            ft.Tab(text="Cond. Comerciais", content=comercial_tab),
            ft.Tab(text="Dados Complementares", content=complementares_tab),
        ],
        expand=True
    )

    # --- Ações ---
    def on_save(e):
        print("Salvar Proposta - Dados Gerais:", 
              cnpj_field.value, razao_social_field.value, 
              inicio_suprimento_field.value, fim_suprimento_field.value)
        print("Salvar Proposta - Dados Comerciais:", form_data["commercial_conditions"])
        
        screen.page.show_snack_bar(ft.SnackBar(ft.Text("Proposta salva (Simulação)!"), bgcolor=ft.Colors.GREEN_600))
        screen.navigation.go("/comercializacao", params={"submenu": "propostas"})

    def on_cancel(e):
        screen.navigation.go("/comercializacao", params={"submenu": "propostas"})

    actions_row = ft.Row(
        controls=[
            ft.ElevatedButton("Cancelar", icon=ft.Icons.CANCEL, on_click=on_cancel, bgcolor=ft.Colors.GREY_500, color=ft.Colors.WHITE),
            ft.ElevatedButton("Salvar", icon=ft.Icons.CHECK, on_click=on_save, bgcolor=ft.Colors.GREEN_600, color=ft.Colors.WHITE),
        ],
        alignment=ft.MainAxisAlignment.END,
        spacing=10
    )

    return ft.Container(
        expand=True,
        padding=20,
        bgcolor=ft.Colors.WHITE,
        border_radius=10,
        content=ft.Column(
            controls=[
                ft.Text("Nova Proposta", size=24, weight=ft.FontWeight.BOLD),
                tabs,
                ft.Divider(),
                actions_row
            ],
            spacing=10
        )
    )

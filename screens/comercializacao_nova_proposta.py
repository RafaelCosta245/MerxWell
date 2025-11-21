from typing import Any, Dict, Optional, List
from datetime import datetime
import flet as ft
import requests
from scripts.database import create_record

# Constantes de horas por mês (simplificado)
HOURS_PER_MONTH = [744, 672, 744, 720, 744, 720, 744, 744, 720, 744, 720, 744]
MESES_KEYS = ["january", "february", "march", "april", "may", "june", "july", "august", "september", "october", "november", "december"]
MESES_LABELS = ["Jan", "Fev", "Mar", "Abr", "Mai", "Jun", "Jul", "Ago", "Set", "Out", "Nov", "Dez"]

# --- Helpers de Validação e Máscara (CNPJ) ---
def validar_cnpj(cnpj: str) -> bool:
    cnpj = ''.join(filter(str.isdigit, cnpj))
    if len(cnpj) != 14 or cnpj == cnpj[0] * 14:
        return False
    peso = [5, 4, 3, 2, 9, 8, 7, 6, 5, 4, 3, 2]
    soma = sum(int(cnpj[i]) * peso[i] for i in range(12))
    resto = soma % 11
    digito1 = 0 if resto < 2 else 11 - resto
    if int(cnpj[12]) != digito1:
        return False
    peso = [6, 5, 4, 3, 2, 9, 8, 7, 6, 5, 4, 3, 2]
    soma = sum(int(cnpj[i]) * peso[i] for i in range(13))
    resto = soma % 11
    digito2 = 0 if resto < 2 else 11 - resto
    return int(cnpj[13]) == digito2

def consultar_cnpj_api(cnpj: str, razao_social_field: ft.TextField, page: ft.Page):
    # Limpa formatação
    cnpj_limpo = ''.join(filter(str.isdigit, cnpj))
    
    # Chave da API (Hardcoded conforme instructions/api_cnpj.py - idealmente viria de env var)
    API_KEY = "4e364762-1c62-4db1-b2e9-d1f7bbee33c4-64a76f78-b79f-43a7-acc2-0a2d2825e2df"
    url = f"https://api.cnpja.com.br/companies/{cnpj_limpo}"
    headers = {"Authorization": API_KEY, "Accept": "application/json"}
    
    print(f"[CNPJ API] Consultando {cnpj_limpo}...")
    
    def _request():
        try:
            r = requests.get(url, headers=headers, timeout=10)
            r.raise_for_status()
            dados = r.json()
            razao = dados.get("name") or dados.get("razao_social") or ""
            if razao:
                razao_social_field.value = razao
                razao_social_field.update()
                print(f"[CNPJ API] Razão Social encontrada: {razao}")
            else:
                print("[CNPJ API] Razão Social não encontrada no JSON.")
        except Exception as e:
            print(f"[CNPJ API] Erro: {e}")

    # Executar em thread separada para não travar UI? 
    # O Flet roda handlers em threads, então requests síncrono aqui pode travar levemente se demorar.
    # Para simplicidade, vamos manter direto, mas idealmente seria async ou thread.
    _request()

# --- Helpers de Validação e Máscara (Data) ---
def validar_data(data: str) -> bool:
    data_limpa = ''.join(filter(str.isdigit, data))
    if len(data_limpa) != 8:
        return False
    try:
        dia = int(data_limpa[:2])
        mes = int(data_limpa[2:4])
        ano = int(data_limpa[4:8])
        datetime(ano, mes, dia)
        return True
    except ValueError:
        return False

def _parse_date_iso(date_str: str) -> Optional[str]:
    """Converte dd/mm/aaaa para aaaa-mm-dd."""
    if not date_str:
        return None
    try:
        # Remove caracteres não numéricos para garantir
        clean_date = ''.join(filter(str.isdigit, date_str))
        if len(clean_date) != 8:
            return None
        dia = int(clean_date[:2])
        mes = int(clean_date[2:4])
        ano = int(clean_date[4:8])
        return f"{ano:04d}-{mes:02d}-{dia:02d}"
    except ValueError:
        return None

def _parse_float(value: Any) -> Optional[float]:
    """Converte string com vírgula ou ponto para float."""
    if value is None or value == "":
        return None
    if isinstance(value, (int, float)):
        return float(value)
    try:
        return float(str(value).replace(",", "."))
    except ValueError:
        return None

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
        "submercado": "NE", # Default
        "inicio_suprimento": "",
        "fim_suprimento": "",
        "tipo_energia": "I5", # Default
        "modulacao": None,
        "data_faturamento": "",
        "garantia": "Seguro Garantia", # Default
        "qty_meses": "2", # Default
        "data_base": datetime.now().strftime("%m/%Y"), # Default
        "validade_proposta": datetime.now().strftime("%d/%m/%Y 18:00"), # Default
        "commercial_conditions": {} 
    }
    
    # Referências para a tabela comercial
    commercial_table_ref = ft.Ref[ft.Column]()
    commercial_rows_refs = [] 

    # --- Handlers de Máscara ---
    def on_cnpj_change(e):
        valor = ''.join(filter(str.isdigit, e.control.value))
        valor = valor[:14]
        valor_formatado = ''
        if len(valor) > 0: valor_formatado = valor[:2]
        if len(valor) > 2: valor_formatado += '.' + valor[2:5]
        if len(valor) > 5: valor_formatado += '.' + valor[5:8]
        if len(valor) > 8: valor_formatado += '/' + valor[8:12]
        if len(valor) > 12: valor_formatado += '-' + valor[12:14]
        
        e.control.value = valor_formatado
        
        if len(valor) == 14:
            if validar_cnpj(valor):
                e.control.error_text = None
                e.control.border_color = ft.Colors.GREEN
                # Busca API
                consultar_cnpj_api(valor, razao_social_field, screen.page)
            else:
                e.control.error_text = "CNPJ inválido"
                e.control.border_color = ft.Colors.RED
        else:
            e.control.error_text = None
            e.control.border_color = None
        
        e.control.update()

    # --- Helpers de Data (Range) ---
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
        
        try:
            if campo in ["price", "flex", "sazo", "volume"] or campo in MESES_KEYS:
                val_str = str(valor).replace(',', '.')
                val_float = float(val_str) if val_str else None
                form_data["commercial_conditions"][ano][campo] = val_float
                
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
        
        snackbar = ft.SnackBar(ft.Text("Dados replicados com sucesso!"), bgcolor=ft.Colors.GREEN_600)
        screen.page.overlay.append(snackbar)
        snackbar.open = True
        screen.page.update()

    commercial_tab_content = ft.Container(padding=10) 
    
    def gerar_tabela_comercial():
        commercial_rows_refs.clear()
        years = _get_years_range(inicio_suprimento_field.value, fim_suprimento_field.value)
        
        if not years:
            # Se não tiver anos válidos, limpa a tabela ou mostra mensagem
            commercial_tab_content.content = ft.Text("Preencha o período de suprimento corretamente na aba 'Dados Gerais'.", color=ft.Colors.RED_500)
            commercial_tab_content.update()
            return

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
            
            # Recuperar dados existentes do form_data
            dados_ano = form_data["commercial_conditions"].get(ano, {})
            
            # Campos
            preco = criar_campo_tabela(80, value=dados_ano.get('price'), on_change=lambda e, a=ano: atualizar_dados_comerciais(a, 'price', e.control.value))
            flex = criar_campo_tabela(80, value=dados_ano.get('flex'), on_change=lambda e, a=ano: atualizar_dados_comerciais(a, 'flex', e.control.value))
            sazo = criar_campo_tabela(80, value=dados_ano.get('sazo'), on_change=lambda e, a=ano: atualizar_dados_comerciais(a, 'sazo', e.control.value))
            vol = criar_campo_tabela(80, value=dados_ano.get('volume'), on_change=lambda e, a=ano: atualizar_dados_comerciais(a, 'volume', e.control.value))
            flat = ft.Switch(value=False, height=30, active_color=ft.Colors.ORANGE_600, on_change=lambda e, a=ano: on_flat_change(e, a))
            
            refs.update({'preco': preco, 'flex': flex, 'sazo': sazo, 'volume': vol, 'flat': flat, 'meses': []})
            
            meses_controls = []
            for mk in MESES_KEYS:
                mc = criar_campo_tabela(70, value=dados_ano.get(mk), on_change=lambda e, a=ano, k=mk: atualizar_dados_comerciais(a, k, e.control.value))
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

        commercial_tab_content.content = ft.Column(controls=rows_controls, spacing=5, scroll=ft.ScrollMode.ALWAYS)
        commercial_tab_content.update()

    def on_date_change(e):
        valor = ''.join(filter(str.isdigit, e.control.value))
        valor = valor[:8]
        valor_formatado = ''
        if len(valor) > 0: valor_formatado = valor[:2]
        if len(valor) > 2: valor_formatado += '/' + valor[2:4]
        if len(valor) > 4: valor_formatado += '/' + valor[4:8]
        
        e.control.value = valor_formatado
        
        if len(valor) == 8:
            if validar_data(valor):
                e.control.error_text = None
                e.control.border_color = ft.Colors.GREEN
                # Tenta gerar tabela se ambas as datas estiverem preenchidas e válidas
                v_inicio = ''.join(filter(str.isdigit, inicio_suprimento_field.value))
                v_fim = ''.join(filter(str.isdigit, fim_suprimento_field.value))
                if len(v_inicio) == 8 and len(v_fim) == 8 and validar_data(v_inicio) and validar_data(v_fim):
                     gerar_tabela_comercial()
            else:
                e.control.error_text = "Data inválida"
                e.control.border_color = ft.Colors.RED
        else:
            e.control.error_text = None
            e.control.border_color = None
            
        e.control.update()

    # --- Aba 1: Dados Gerais ---
    cnpj_field = ft.TextField(
        label="CNPJ", 
        width=200,
        on_change=on_cnpj_change,
        hint_text="00.000.000/0000-00"
    )
    razao_social_field = ft.TextField(label="Razão Social", width=600)
    
    submercado_dd = ft.Dropdown(
        label="Submercado",
        width=cnpj_field.width,
        value="NE", # Default
        options=[
            ft.dropdown.Option("SE/CO"),
            ft.dropdown.Option("NE"),
            ft.dropdown.Option("N"),
            ft.dropdown.Option("S"),
        ]
    )
    
    inicio_suprimento_field = ft.TextField(
        label="Início Suprimento",
        width=cnpj_field.width,
        hint_text="01/01/2026",
        on_change=on_date_change
    )
    fim_suprimento_field = ft.TextField(
        label="Fim Suprimento",
        width=cnpj_field.width,
        hint_text="31/12/2030",
        on_change=on_date_change
    )
    
    tipo_energia_dd = ft.Dropdown(
        label="Tipo de Energia",
        width=cnpj_field.width,
        value="I5", # Default
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
        label="Modulação", width=200,
        options=[ft.dropdown.Option("FLAT"), ft.dropdown.Option("CARGA")],
        value="FLAT", # Default]
    )
    data_fat_pag_field = ft.TextField(label="Data de pagamento (du)", width=200, value=6)
    
    garantia_dd = ft.Dropdown(
        label="Garantia", width=200,
        value="Seguro Garantia", # Default
        options=[ft.dropdown.Option("Seguro Garantia"), ft.dropdown.Option("Carta fiança"), ft.dropdown.Option("Todas")]
    )
    
    qty_meses_field = ft.TextField(label="Qty_meses", width=200, value="2") # Default
    
    data_base_field = ft.TextField(
        label="Data Base", 
        width=200,
        value=datetime.now().strftime("%m/%Y") # Default
    )
    
    validade_proposta_field = ft.TextField(
        label="Validade da proposta", 
        width=200,
        value=datetime.now().strftime("%d/%m/%Y 17:00 h") # Default
    )

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
        tabs=[
            ft.Tab(text="Dados Gerais", content=dados_gerais_tab),
            ft.Tab(text="Cond. Comerciais", content=comercial_tab),
            ft.Tab(text="Dados Complementares", content=complementares_tab),
        ],
        expand=True
    )

    # --- Ações ---
    def on_save(e):
        # 1. Validação Básica
        required_fields = [
            (cnpj_field, "CNPJ"),
            (razao_social_field, "Razão Social"),
            (inicio_suprimento_field, "Início Suprimento"),
            (fim_suprimento_field, "Fim Suprimento")
        ]
        for field, name in required_fields:
            if not field.value:
                snackbar = ft.SnackBar(ft.Text(f"Campo obrigatório: {name}"), bgcolor=ft.Colors.RED_600)
                screen.page.overlay.append(snackbar)
                snackbar.open = True
                screen.page.update()
                return

        try:
            # 2. Montar Payload da Proposta (Etapa 1)
            proposal_payload = {
                "customer_cnpj": ''.join(filter(str.isdigit, cnpj_field.value)), # Remove máscara
                "customer_name": razao_social_field.value,
                "submarket": submercado_dd.value,
                "energy_type": tipo_energia_dd.value,
                "supply_start": _parse_date_iso(inicio_suprimento_field.value),
                "supply_end": _parse_date_iso(fim_suprimento_field.value),
                "modulation": modulacao_dd.value,
                "billing_due_day": int(str(data_fat_pag_field.value)) if str(data_fat_pag_field.value).isdigit() else None,
                "guarantee_type": garantia_dd.value,
                "guarantee_months": int(str(qty_meses_field.value)) if str(qty_meses_field.value).isdigit() else None,
                "reference_date": data_base_field.value,
                "proposal_validity": validade_proposta_field.value,
                "status": "PENDING"
            }

            print(f"[DEBUG] Saving proposal: {proposal_payload}")
            
            # Salvar Proposta
            res_proposal = create_record("proposals", proposal_payload)
            if isinstance(res_proposal, list) and len(res_proposal) > 0:
                proposal_id = res_proposal[0].get('id')
            elif isinstance(res_proposal, dict):
                proposal_id = res_proposal.get('id')
            else:
                raise Exception("Falha ao obter ID da proposta salva.")

            if not proposal_id:
                raise Exception("ID da proposta não retornado pelo banco.")

            # Log Sucesso Proposta
            create_record("proposal_logs", {"proposal_id": proposal_id, "message": "Proposal created successfully"})

            # 3. Salvar Sazonalidades (Etapa 2)
            years = _get_years_range(inicio_suprimento_field.value, fim_suprimento_field.value)
            
            for ano in years:
                dados_ano = form_data["commercial_conditions"].get(ano, {})
                
                sazo_payload = {
                    "proposal_id": proposal_id,
                    "year": ano,
                    "price": _parse_float(dados_ano.get("price")),
                    "flex": _parse_float(dados_ano.get("flex")),
                    "seasonality": _parse_float(dados_ano.get("sazo")),
                    "average_volume": _parse_float(dados_ano.get("volume")),
                    "is_flat": False, # O switch na UI é apenas visual/helper, mas podemos tentar inferir ou pegar do ref se precisarmos salvar o estado. Instrução diz "campo Flat".
                }
                
                # Adicionar meses
                for mk in MESES_KEYS:
                    sazo_payload[mk] = _parse_float(dados_ano.get(mk))

                create_record("proposal_seasonalities", sazo_payload)

            # Log Sucesso Sazonalidades
            create_record("proposal_logs", {"proposal_id": proposal_id, "message": "All seasonalities saved successfully"})

            snackbar = ft.SnackBar(ft.Text("Proposta salva com sucesso!"), bgcolor=ft.Colors.GREEN_600)
            screen.page.overlay.append(snackbar)
            snackbar.open = True
            screen.page.update()
            
            screen.navigation.go("/comercializacao", params={"submenu": "propostas"})

        except Exception as ex:
            print(f"[ERROR] Erro ao salvar proposta: {ex}")
            snackbar = ft.SnackBar(ft.Text(f"Erro ao salvar: {str(ex)}"), bgcolor=ft.Colors.RED_600)
            screen.page.overlay.append(snackbar)
            snackbar.open = True
            screen.page.update()
            
            # Tenta logar erro se tiver ID
            if 'proposal_id' in locals() and proposal_id:
                try:
                    create_record("proposal_logs", {"proposal_id": proposal_id, "message": f"Error: {str(ex)}"})
                except:
                    pass

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

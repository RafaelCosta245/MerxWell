from typing import Any, Dict, Optional, List
import flet as ft
from datetime import datetime, date

import pandas as pd
import base64
import io

from scripts.database import read_records, create_record, delete_records

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
    
    # Mapeamento de Submercados (Planilha -> App)
    submercado_map = {
        "SUDESTE": "SE/CO",
        "NORDESTE": "NE",
        "NORTE": "N",
        "SUL": "S"
    }

    # Armazenar dados do formulário
    # Estrutura: { ano: { (submercado, tipo_energia): valor } }
    form_data = {}
    
    # Armazenar referências aos campos de texto para atualização automática
    # Estrutura: { (ano, submercado, tipo_energia): TextField }
    field_refs = {}

    # --- Componentes de Configuração (Trader e Data) ---
    
    # Carregar traders
    traders_db = read_records("traders", filters=None)
    traders_db.sort(key=lambda t: (t.get("name") or "").lower())
    
    trader_options = [ft.dropdown.Option(key=str(t["id"]), text=t["name"]) for t in traders_db if t.get("id") and t.get("name")]
    
    trader_dd = ft.Dropdown(
        label="Comercializadora",
        hint_text="Selecione a comercializadora",
        options=trader_options,
        width=400,
    )
    
    # Configuração de localização para português do Brasil
    def configure_locale(page):
        if hasattr(page, 'locale_configuration') and page.locale_configuration is None:
            page.locale_configuration = ft.LocaleConfiguration(
                supported_locales=[
                    ft.Locale("pt", "BR"),
                    ft.Locale("en", "US")
                ],
                current_locale=ft.Locale("pt", "BR")
            )

    # Data de Referência
    selected_date = date.today()
    
    date_picker = ft.DatePicker(
        first_date=datetime(2020, 1, 1),
        last_date=datetime(2030, 12, 31),
    )

    def on_date_change(e):
        nonlocal selected_date
        if date_picker.value:
            selected_date = date_picker.value.date()
            date_button.text = selected_date.strftime("%d/%m/%Y")
            date_button.update()
            
    date_picker.on_change = on_date_change

    def open_date_picker(e):
        configure_locale(screen.page)
        if date_picker not in screen.page.overlay:
            screen.page.overlay.append(date_picker)
            screen.page.update()
        screen.page.open(date_picker)
    
    date_button = ft.ElevatedButton(
        text=selected_date.strftime("%d/%m/%Y"),
        icon=ft.Icons.CALENDAR_MONTH,
        on_click=open_date_picker,
        style=ft.ButtonStyle(
            shape=ft.RoundedRectangleBorder(radius=8),
            padding=ft.padding.symmetric(horizontal=20, vertical=0), # Ajustado padding vertical
            color=ft.Colors.GREY_800,
            bgcolor=ft.Colors.WHITE,
            side=ft.BorderSide(1, ft.Colors.GREY_400), # Borda para combinar com dropdown
        ),
        height=50, # Mesma altura do dropdown (aproximadamente)
    )

    config_row = ft.Row(
        controls=[
            trader_dd,
            ft.Container(width=20),
            ft.Column(
                controls=[
                    # Label vazia para alinhar com o label do dropdown se necessário, 
                    # ou usar o label do próprio botão se fosse um TextField.
                    # Aqui vamos simular o label acima do botão.
                    ft.Text("Data de Referência", size=12, color=ft.Colors.GREY_700),
                    date_button,
                ],
                spacing=5,
            )
        ],
        alignment=ft.MainAxisAlignment.START,
        vertical_alignment=ft.CrossAxisAlignment.END, # Alinha base dos controles
    )

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
        
        field = ft.TextField(
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
        
        # Guardar referência
        field_refs[(ano, submercado, tipo_energia)] = field
        return field
    
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
    
    # --- Lógica do FilePicker (Forward SRN) ---
    
    def on_file_result(e: ft.FilePickerResultEvent):
        if not e.files:
            return
            
        file_obj = e.files[0]
        print(f"Arquivo selecionado: {file_obj.name}")
        
        try:
            if file_obj.path:
                df = pd.read_excel(file_obj.path)
            else:
                raise Exception("Não foi possível ler o caminho do arquivo local.")

            # Processamento do DataFrame
            dados_lidos = {}

            for col in df.columns:
                if col == "PRODUTO":
                    continue
                
                parts = col.split("_")
                if len(parts) < 2:
                    continue
                    
                sub_planilha = parts[0]
                tipo_planilha = parts[1]
                
                sub_app = submercado_map.get(sub_planilha)
                if not sub_app:
                    continue
                
                if tipo_planilha not in tipos_energia:
                    continue
                
                for _, row in df.iterrows():
                    try:
                        ano = int(row["PRODUTO"])
                        val = float(row[col])
                        
                        if ano not in dados_lidos:
                            dados_lidos[ano] = {}
                        
                        dados_lidos[ano][(sub_app, tipo_planilha)] = val
                        
                    except Exception as ex:
                        print(f"Erro ao ler linha: {ex}")
                        continue

            # --- Lógica de Cálculo para I1 e CQ5 ---
            # I1 = I5 + 170
            # CQ5 = I5 - 2
            
            for ano in anos:
                if ano not in dados_lidos:
                    dados_lidos[ano] = {}
                
                for sub in submercados:
                    # Verifica se temos I5
                    i5_val = dados_lidos[ano].get((sub, "I5"))
                    
                    if i5_val is not None:
                        # Calcular I1 se não existir
                        if (sub, "I1") not in dados_lidos[ano]:
                            dados_lidos[ano][(sub, "I1")] = i5_val + 170.0
                        
                        # Calcular CQ5 se não existir
                        if (sub, "CQ5") not in dados_lidos[ano]:
                            dados_lidos[ano][(sub, "CQ5")] = i5_val - 2.0

            # Atualizar UI e form_data
            count_updates = 0
            for ano, dados_ano in dados_lidos.items():
                if ano not in form_data:
                    form_data[ano] = {}
                    
                for (sub, tipo), valor in dados_ano.items():
                    # Atualiza form_data
                    form_data[ano][(sub, tipo)] = valor
                    
                    # Atualiza UI se o campo existir
                    if (ano, sub, tipo) in field_refs:
                        # Formata com 2 casas decimais e vírgula
                        field_refs[(ano, sub, tipo)].value = f"{valor:.2f}".replace('.', ',')
                        count_updates += 1
            
            screen.page.update()
            
            snackbar = ft.SnackBar(
                content=ft.Text(f"Importação concluída! {count_updates} campos atualizados."),
                bgcolor=ft.Colors.GREEN_600,
            )
            screen.page.overlay.append(snackbar)
            snackbar.open = True
            screen.page.update()

        except Exception as ex:
            snackbar = ft.SnackBar(
                content=ft.Text(f"Erro ao processar arquivo: {ex}"),
                bgcolor=ft.Colors.RED_600,
            )
            screen.page.overlay.append(snackbar)
            snackbar.open = True
            screen.page.update()

    file_picker = ft.FilePicker(on_result=on_file_result)
    screen.page.overlay.append(file_picker)

    # Funções dos botões
    def on_save(e):
        print("Salvando dados de preços...")
        
        # Validação
        if not trader_dd.value:
            snackbar = ft.SnackBar(
                content=ft.Text("Selecione uma comercializadora!"),
                bgcolor=ft.Colors.RED_600,
            )
            screen.page.overlay.append(snackbar)
            snackbar.open = True
            screen.page.update()
            return

        trader_id = trader_dd.value
        snapshot_date_str = selected_date.isoformat()
        
        # Função interna para realizar o salvamento (com ou sem deleção prévia)
        def perform_save(old_snapshot_id=None):
            try:
                if old_snapshot_id:
                    print(f"Deletando snapshot antigo: {old_snapshot_id}")
                    # Primeiro deletar preços associados (por segurança)
                    delete_records("energy_prices", {"snapshot_id": old_snapshot_id})
                    # Depois deletar o snapshot
                    delete_records("energy_price_snapshots", {"id": old_snapshot_id})
                
                # 1. Criar Snapshot
                snapshot_data = {
                    "trader_id": trader_id,
                    "snapshot_date": snapshot_date_str
                }
                
                print(f"Criando snapshot: {snapshot_data}")
                snapshot_res = create_record("energy_price_snapshots", snapshot_data)
                
                if not snapshot_res:
                    raise Exception("Falha ao criar snapshot.")
                    
                snapshot_id = snapshot_res[0]["id"]
                print(f"Snapshot criado: {snapshot_id}")
                
                # 2. Inserir Preços
                prices_to_insert = []
                for ano, dados_ano in form_data.items():
                    for (sub, tipo), valor in dados_ano.items():
                        if valor is not None:
                            prices_to_insert.append({
                                "snapshot_id": snapshot_id,
                                "year": ano,
                                "energy_type": tipo,
                                "submarket": sub,
                                "price": valor
                            })
                
                if prices_to_insert:
                    print(f"Inserindo {len(prices_to_insert)} preços...")
                    BATCH_SIZE = 1000
                    for i in range(0, len(prices_to_insert), BATCH_SIZE):
                        batch = prices_to_insert[i:i + BATCH_SIZE]
                        create_record("energy_prices", batch)
                
                snackbar = ft.SnackBar(
                    content=ft.Text(f"Sucesso! {len(prices_to_insert)} preços salvos."),
                    bgcolor=ft.Colors.GREEN_600,
                )
                screen.page.overlay.append(snackbar)
                snackbar.open = True
                screen.page.update()
                
                # Voltar para a tela anterior
                screen.navigation.go(
                    "/comercializacao",
                    params={"submenu": "precos"},
                )
                
            except Exception as ex:
                print(f"Erro ao salvar: {ex}")
                snackbar = ft.SnackBar(
                    content=ft.Text(f"Erro ao salvar: {ex}"),
                    bgcolor=ft.Colors.RED_600,
                )
                screen.page.overlay.append(snackbar)
                snackbar.open = True
                screen.page.update()

        # Verificar duplicidade
        try:
            existing_snapshots = read_records(
                "energy_price_snapshots", 
                filters={"trader_id": trader_id, "snapshot_date": snapshot_date_str}
            )
            
            if existing_snapshots:
                old_id = existing_snapshots[0]["id"]
                
                def close_dlg(e):
                    screen.page.close(dlg)
                    
                def confirm_overwrite(e):
                    screen.page.close(dlg)
                    perform_save(old_snapshot_id=old_id)
                
                dlg = ft.AlertDialog(
                    modal=True,
                    title=ft.Text("Curva já existente"),
                    content=ft.Text("Já existe uma curva salva para esta comercializadora nesta data.\nDeseja sobrescrever os dados existentes?"),
                    actions=[
                        ft.TextButton("Cancelar", on_click=close_dlg),
                        ft.TextButton("Sobrescrever", on_click=confirm_overwrite, style=ft.ButtonStyle(color=ft.Colors.RED)),
                    ],
                    actions_alignment=ft.MainAxisAlignment.END,
                )
                screen.page.open(dlg)
            else:
                perform_save()
                
        except Exception as ex:
            print(f"Erro ao verificar duplicidade: {ex}")
            snackbar = ft.SnackBar(
                content=ft.Text(f"Erro ao verificar duplicidade: {ex}"),
                bgcolor=ft.Colors.RED_600,
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
        file_picker.pick_files(
            allow_multiple=False,
            allowed_extensions=["xls", "xlsx"],
            dialog_title="Selecione a planilha Forward SRN"
        )
    
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
                config_row, # Adicionado linha de configuração (Trader e Data)
                ft.Container(height=12),
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

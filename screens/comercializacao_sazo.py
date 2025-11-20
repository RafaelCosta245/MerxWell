import flet as ft
from datetime import datetime
from typing import Any, Dict, Optional, List
from scripts.database import read_records, create_record, update_record

# Constantes de horas por mês
HOURS_PER_MONTH = [
    744,  # Jan
    672,  # Fev (28 dias - simplificado)
    744,  # Mar
    720,  # Abr
    744,  # Mai
    720,  # Jun
    744,  # Jul
    744,  # Ago
    720,  # Set
    744,  # Out
    720,  # Nov
    744,  # Dez
]

def create_sazo_content(screen: Any, contract_id: str, start_date: Any, end_date: Any) -> ft.Control:
    """
    Cria o formulário de sazonalidade para um contrato específico.
    
    Args:
        screen: Referência à tela principal para navegação
        contract_id: ID do contrato
        start_date: Data de início do contrato
        end_date: Data de fim do contrato
    """
    
    def _get_year(value: Any) -> Optional[int]:
        if value is None:
            return None
        if isinstance(value, int):
            return value
        s = str(value)
        if not s:
            return None
        try:
            # Tenta parse ISO completo
            dt = datetime.fromisoformat(s.replace("Z", "+00:00"))
            return dt.year
        except Exception:
            # Fallback para string YYYY...
            if len(s) >= 4:
                try:
                    return int(s[:4])
                except ValueError:
                    pass
            return None

    ano_inicio = _get_year(start_date)
    ano_fim = _get_year(end_date)

    # Fallback se datas inválidas
    if ano_inicio is None:
        ano_inicio = datetime.now().year
    if ano_fim is None:
        ano_fim = ano_inicio + 1
        
    # Garante ordem correta
    if ano_inicio > ano_fim:
        ano_inicio, ano_fim = ano_fim, ano_inicio

    # Carregar dados existentes do banco
    existing_data_map = {}
    try:
        records = read_records("contracts_seasonalities", {"contract_id": contract_id})
        for r in records:
            y = r.get("year")
            if y:
                existing_data_map[int(y)] = r
    except Exception as e:
        print(f"Erro ao carregar sazonalidades: {e}")
        screen.page.show_snack_bar(
            ft.SnackBar(content=ft.Text(f"Erro ao carregar dados: {e}"), bgcolor=ft.Colors.RED_600)
        )

    # Armazenar dados do formulário
    # Estrutura: { ano: { 'year': ..., 'contract_id': ..., 'db_id': ..., 'price_energy': ..., ... } }
    form_data = {}

    # Meses
    meses = ["Jan", "Fev", "Mar", "Abr", "Mai", "Jun", "Jul", "Ago", "Set", "Out", "Nov", "Dez"]
    meses_keys = ["january", "february", "march", "april", "may", "june", "july", "august", "september", "october",
                  "november", "december"]

    # Armazenar referências das linhas para atualizações de UI
    linhas_refs = []

    def criar_campo(width=80, on_change=None, value=None):
        return ft.TextField(
            value=str(value) if value is not None else "",
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

    def atualizar_dados(ano, campo, valor):
        if ano not in form_data:
            form_data[ano] = {'year': ano, 'contract_id': contract_id}

        if campo in ['price_energy', 'medium_volume'] or campo in meses_keys:
            try:
                # Substitui vírgula por ponto para conversão
                val_str = str(valor).replace(',', '.')
                val_float = float(val_str) if val_str else None
                form_data[ano][campo] = val_float
                
                # Lógica do Flat Switch
                # Se alterou medium_volume e flat está ativo, recalcula meses
                if campo == 'medium_volume':
                    # Encontrar a referência da linha
                    linha_ref = next((r for r in linhas_refs if r['ano'] == ano), None)
                    if linha_ref and linha_ref['flat'].value:
                        aplicar_flat(ano, linha_ref, val_float)

            except ValueError:
                form_data[ano][campo] = None
        else:
            form_data[ano][campo] = valor

    def aplicar_flat(ano, linha_ref, volume_medio):
        if volume_medio is None:
            return
        
        for idx, mes_key in enumerate(meses_keys):
            horas = HOURS_PER_MONTH[idx]
            valor_mes = volume_medio * horas
            
            # Atualiza form_data
            form_data[ano][mes_key] = valor_mes
            
            # Atualiza UI
            if idx < len(linha_ref['meses']):
                linha_ref['meses'][idx].value = f"{valor_mes:.2f}"
        
        screen.page.update()

    def on_flat_change(e, ano):
        is_flat = e.control.value
        if is_flat:
            # Pega o volume médio atual
            vol_medio = form_data.get(ano, {}).get('medium_volume')
            if vol_medio is not None:
                linha_ref = next((r for r in linhas_refs if r['ano'] == ano), None)
                if linha_ref:
                    aplicar_flat(ano, linha_ref, vol_medio)

    def limpar_linha(e, ano):
        linha_ref = next((r for r in linhas_refs if r['ano'] == ano), None)
        if not linha_ref:
            return

        # Limpar dados no dicionário
        if ano in form_data:
            # Mantém chaves essenciais
            db_id = form_data[ano].get('db_id')
            form_data[ano] = {'year': ano, 'contract_id': contract_id}
            if db_id:
                form_data[ano]['db_id'] = db_id

        # Limpar UI
        linha_ref['preco'].value = ""
        linha_ref['volume'].value = ""
        linha_ref['garantia'].value = False
        linha_ref['flat'].value = False
        for campo in linha_ref['meses']:
            campo.value = ""
        
        screen.page.update()

    def copiar_primeira_linha(e):
        if not linhas_refs or len(linhas_refs) < 2:
            return

        primeira_linha = linhas_refs[0]
        ano_origem = primeira_linha['ano']
        
        # Dados da origem
        dados_origem = form_data.get(ano_origem, {})

        # Copiar para todas as linhas abaixo
        for i in range(1, len(linhas_refs)):
            linha = linhas_refs[i]
            ano_destino = linha['ano']

            # Copiar UI
            linha['preco'].value = primeira_linha['preco'].value
            linha['volume'].value = primeira_linha['volume'].value
            linha['garantia'].value = primeira_linha['garantia'].value
            # Não copiamos o estado do switch Flat, mas copiamos os valores resultantes
            # linha['flat'].value = primeira_linha['flat'].value 
            
            for j in range(12):
                linha['meses'][j].value = primeira_linha['meses'][j].value
            
            # Atualizar form_data
            if ano_destino not in form_data:
                form_data[ano_destino] = {'year': ano_destino, 'contract_id': contract_id}
            
            # Preservar db_id se existir
            db_id = form_data[ano_destino].get('db_id')
            
            # Copiar valores
            for key in ['price_energy', 'medium_volume', 'financial_guarantee'] + meses_keys:
                if key in dados_origem:
                    form_data[ano_destino][key] = dados_origem[key]
            
            if db_id:
                form_data[ano_destino]['db_id'] = db_id

        screen.page.update()
        screen.page.show_snack_bar(
            ft.SnackBar(
                content=ft.Text("✅ Dados copiados para todas as linhas!"),
                bgcolor=ft.Colors.GREEN_600,
            )
        )

    def criar_linha_ano(ano, is_first=False):
        # Recuperar dados existentes se houver
        dados_existentes = existing_data_map.get(ano, {})
        
        # Inicializar form_data com dados existentes
        if dados_existentes:
            form_data[ano] = dados_existentes.copy()
            # Garantir que year e contract_id estão corretos (devem estar se vieram do banco)
            form_data[ano]['year'] = ano
            form_data[ano]['contract_id'] = contract_id
            form_data[ano]['db_id'] = dados_existentes.get('id') # Guardar ID para update

        campos_meses = []
        refs = {'ano': ano}

        # Campo preço
        val_preco = dados_existentes.get('price_energy')
        preco_field = criar_campo(
            width=100,
            value=val_preco,
            on_change=lambda e: atualizar_dados(ano, 'price_energy', e.control.value)
        )
        refs['preco'] = preco_field

        # Campo Volume MWm
        val_volume = dados_existentes.get('medium_volume')
        volume_field = criar_campo(
            width=100,
            value=val_volume,
            on_change=lambda e: atualizar_dados(ano, 'medium_volume', e.control.value)
        )
        refs['volume'] = volume_field

        # Switch garantia
        val_garantia = dados_existentes.get('financial_guarantee', False)
        garantia_switch = ft.Switch(
            value=bool(val_garantia),
            active_color=ft.Colors.BLUE_600,
            height=30,
            on_change=lambda e: atualizar_dados(ano, 'financial_guarantee', e.control.value)
        )
        refs['garantia'] = garantia_switch

        # Switch Flat
        flat_switch = ft.Switch(
            value=False, # Não salvamos estado do flat no banco, sempre inicia desligado
            active_color=ft.Colors.ORANGE_600,
            height=30,
            on_change=lambda e: on_flat_change(e, ano)
        )
        refs['flat'] = flat_switch

        # Campos dos meses
        for mes_key in meses_keys:
            val_mes = dados_existentes.get(mes_key)
            campo = criar_campo(
                value=val_mes,
                on_change=lambda e, mk=mes_key: atualizar_dados(ano, mk, e.control.value)
            )
            campos_meses.append(campo)
        refs['meses'] = campos_meses

        # Botão de copiar (apenas na primeira linha)
        if is_first:
            botao_copiar = ft.IconButton(
                icon=ft.Icons.CONTENT_COPY,
                icon_color=ft.Colors.BLUE_700,
                tooltip="Copiar dados para todas as linhas abaixo",
                on_click=copiar_primeira_linha,
            )
        else:
            botao_copiar = ft.Container(width=40)

        # Botão Delete
        botao_delete = ft.IconButton(
            icon=ft.Icons.DELETE_OUTLINE,
            icon_color=ft.Colors.RED_400,
            tooltip="Limpar linha",
            on_click=lambda e: limpar_linha(e, ano)
        )

        linha = ft.Row(
            controls=[
                botao_copiar,
                ft.Container(
                    content=ft.Text(str(ano), size=14, weight=ft.FontWeight.BOLD, color=ft.Colors.BLACK),
                    width=60,
                    alignment=ft.alignment.center,
                ),
                preco_field,
                volume_field,
                ft.Container(
                    content=garantia_switch,
                    width=60,
                    alignment=ft.alignment.center,
                ),
                ft.Container(
                    content=flat_switch,
                    width=50,
                    alignment=ft.alignment.center,
                ),
            ] + campos_meses + [botao_delete],
            spacing=5,
            alignment=ft.MainAxisAlignment.START,
        )

        linhas_refs.append(refs)
        return linha

    def salvar_dados(e):
        if not form_data:
            screen.page.show_snack_bar(
                ft.SnackBar(content=ft.Text("⚠ Preencha os dados primeiro!"), bgcolor=ft.Colors.ORANGE_600)
            )
            return

        count_sucesso = 0
        erros = []

        for ano, dados in form_data.items():
            # Verifica se tem dados relevantes para salvar (pelo menos preço ou volume ou algum mês)
            # Se tudo for None, talvez devêssemos ignorar ou limpar?
            # O usuário pediu para salvar. Vamos salvar o que tem.
            
            # Preparar payload
            payload = {
                'year': dados.get('year'),
                'contract_id': dados.get('contract_id'),
                'price_energy': dados.get('price_energy'),
                'medium_volume': dados.get('medium_volume'),
                'financial_guarantee': dados.get('financial_guarantee', False),
            }
            for mk in meses_keys:
                payload[mk] = dados.get(mk)

            db_id = dados.get('db_id')
            
            try:
                if db_id:
                    # Update
                    update_record("contracts_seasonalities", db_id, payload)
                else:
                    # Create
                    # Verifica novamente se já existe (caso de concorrência ou recarregamento sem refresh)
                    # Mas assumindo fluxo normal, se não tinha ID no load, é create.
                    # Porém, contracts_seasonalities não tem unique constraint explícita no schema fornecido,
                    # mas logicamente deveria ser unique(contract_id, year).
                    # Vamos tentar create.
                    res = create_record("contracts_seasonalities", payload)
                    if res and isinstance(res, list) and len(res) > 0:
                         form_data[ano]['db_id'] = res[0].get('id')
                    elif res and isinstance(res, dict):
                         form_data[ano]['db_id'] = res.get('id')

                count_sucesso += 1
            except Exception as ex:
                erros.append(f"Ano {ano}: {str(ex)}")

        if erros:
            print("Erros ao salvar:", erros)
            snackbar = ft.SnackBar(
                content=ft.Text(f"⚠ Erro ao salvar alguns registros. Verifique o console."),
                bgcolor=ft.Colors.RED_600,
            )
            screen.page.overlay.append(snackbar)
            snackbar.open = True
            screen.page.update()
        else:
            snackbar = ft.SnackBar(
                content=ft.Text(f"✅ {count_sucesso} registro(s) salvo(s) com sucesso!"),
                bgcolor=ft.Colors.GREEN_600,
            )
            screen.page.overlay.append(snackbar)
            snackbar.open = True
            screen.page.update()
        
        # Retornar para a tela de contratos
        screen.navigation.go("/comercializacao", params={"submenu": "contratos"})

    def cancelar(e):
        screen.navigation.go("/comercializacao", params={"submenu": "contratos"})

    # Cabeçalho da planilha
    cabecalho = ft.Row(
        controls=[
            ft.Container(width=40),  # Espaço do botão copy
            ft.Container(
                content=ft.Text("Ano", size=12, weight=ft.FontWeight.BOLD, color=ft.Colors.BLACK),
                width=60,
                alignment=ft.alignment.center,
            ),
            ft.Container(
                content=ft.Text("Preço\nR$/MWh", size=11, weight=ft.FontWeight.BOLD, color=ft.Colors.BLACK, text_align=ft.TextAlign.CENTER),
                width=100,
                alignment=ft.alignment.center,
            ),
            ft.Container(
                content=ft.Text("Volume\nMWm", size=11, weight=ft.FontWeight.BOLD, color=ft.Colors.BLACK, text_align=ft.TextAlign.CENTER),
                width=100,
                alignment=ft.alignment.center,
            ),
            ft.Container(
                content=ft.Text("Garantia", size=11, weight=ft.FontWeight.BOLD, color=ft.Colors.BLACK),
                width=60,
                alignment=ft.alignment.center,
            ),
            ft.Container(
                content=ft.Text("Flat", size=11, weight=ft.FontWeight.BOLD, color=ft.Colors.BLACK),
                width=50,
                alignment=ft.alignment.center,
            ),
        ] + [
            ft.Container(
                content=ft.Text(mes, size=12, weight=ft.FontWeight.BOLD, color=ft.Colors.BLACK),
                width=80,
                alignment=ft.alignment.center,
            ) for mes in meses
        ] + [
            ft.Container(width=40) # Espaço botão delete
        ],
        spacing=5,
    )

    # Criar linhas para cada ano
    linhas = []
    for idx, ano in enumerate(range(ano_inicio, ano_fim + 1)):
        linhas.append(criar_linha_ano(ano, is_first=(idx == 0)))

    # Container com scroll duplo
    tabela_container = ft.Container(
        content=ft.Column(
            controls=[
                ft.Container(
                    content=ft.Column(
                        controls=[
                            cabecalho,
                            ft.Divider(height=1, color=ft.Colors.GREY_300),
                            ft.Column(
                                controls=linhas,
                                spacing=2,
                            ),
                        ],
                        spacing=5,
                    ),
                    width=1600, # Largura suficiente para forçar scroll horizontal se necessário
                )
            ],
            scroll=ft.ScrollMode.ALWAYS, # Scroll Vertical
            expand=True,
        ),
        expand=True,
        bgcolor=ft.Colors.WHITE,
        border=ft.border.all(1, ft.Colors.GREY_300),
        border_radius=8,
        padding=10,
        #alignment=ft.MainAxisAlignment.START,
    )
    
    # Wrapper para scroll horizontal
    scroll_horizontal = ft.Row(
        controls=[tabela_container],
        scroll=ft.ScrollMode.ALWAYS,
        expand=True,
    )

    return ft.Container(
        expand=True,
        padding=20,
        bgcolor=ft.Colors.WHITE,
        content=ft.Column(
            controls=[
                # Título e Botões de Ação
                ft.Row(
                    controls=[
                        ft.Text(
                            f"Sazonalidade: Contrato {contract_id} ({ano_inicio}-{ano_fim})",
                            size=20,
                            weight=ft.FontWeight.BOLD,
                            color=ft.Colors.BLACK,
                        ),
                        ft.Row(
                            controls=[
                                ft.ElevatedButton(
                                    "Cancelar",
                                    icon=ft.Icons.CANCEL,
                                    style=ft.ButtonStyle(
                                        color=ft.Colors.WHITE,
                                        bgcolor=ft.Colors.RED_700,
                                        shape=ft.RoundedRectangleBorder(radius=6),
                                    ),
                                    on_click=cancelar,
                                ),
                                ft.ElevatedButton(
                                    "Salvar",
                                    icon=ft.Icons.CHECK,
                                    on_click=salvar_dados,
                                    style=ft.ButtonStyle(
                                        color=ft.Colors.WHITE,
                                        bgcolor=ft.Colors.GREEN_700,
                                        shape=ft.RoundedRectangleBorder(radius=6),
                                    ),
                                ),
                            ],
                            spacing=10,
                        ),
                    ],
                    alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                ),
                #ft.Divider(),
                # Área da tabela com scroll
                scroll_horizontal,
            ],
            spacing=20,
        )
    )

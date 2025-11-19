from __future__ import annotations

from typing import Any, Dict, Optional
from datetime import datetime

import flet as ft

from scripts.database import read_records, create_record, update_record


def _parse_date_br(value: str) -> Optional[str]:
    """Converte 'dd/mm/aaaa' em ISO 'aaaa-mm-dd'. Retorna None se inválido."""
    if not value:
        return None
    try:
        dt = datetime.strptime(value.strip(), "%d/%m/%Y")
        return dt.date().isoformat()
    except Exception:
        return None

def _format_date_br(value: Optional[str]) -> str:
    """Converte ISO 'aaaa-mm-dd' para 'dd/mm/aaaa'. Retorna vazio se None."""
    if not value:
        return ""
    try:
        dt = datetime.fromisoformat(value.replace("Z", "+00:00"))
        return dt.strftime("%d/%m/%Y")
    except Exception:
        return ""


def create_novo_contrato_content(
    screen: Any,
    buyer_filter: Optional[str],
    seller_filter: Optional[str],
    contract_id: Optional[str] = None,
) -> ft.Control:
    """Formulário de novo contrato ou edição para a aba Contratos.

    Ao salvar, cria ou atualiza o registro na tabela `contracts` e volta para a listagem.
    """

    is_editing = bool(contract_id)
    title_text = "Editar Contrato" if is_editing else "Novo Contrato"
    
    existing_data = {}
    if is_editing:
        try:
            records = read_records("contracts", {"id": contract_id})
            if records:
                existing_data = records[0]
        except Exception as e:
            print(f"Erro ao carregar contrato: {e}")

    # ------------------------ Campos básicos ------------------------
    # Comercializadora vinculada (trader_id) e prestador (service_provider)
    print(f"[{title_text}] Carregando formulário...")

    # Carrega lista de traders do banco para popular o dropdown
    traders_db = read_records("traders", filters=None)
    # Ordena por nome para facilitar a busca visual
    traders_db.sort(key=lambda t: (t.get("name") or "").lower())

    trader_options = []
    current_trader_name = None
    
    # Se editando, tenta achar o nome do trader pelo ID
    if is_editing:
        t_id = existing_data.get("trader_id")
        print(f"[{title_text}] Trader ID do contrato: {t_id}")
        
        if t_id:
            for t in traders_db:
                # Comparação segura convertendo para string
                if str(t.get("id")) == str(t_id):
                    current_trader_name = t.get("name")
                    print(f"[{title_text}] Trader encontrado: {current_trader_name}")
                    break
            
            if not current_trader_name:
                print(f"[{title_text}] AVISO: Trader ID {t_id} não encontrado na lista de traders.")

    for t in traders_db:
        name = t.get("name")
        if name:
            trader_options.append(ft.dropdown.Option(str(name)))

    if not trader_options:
        trader_options.append(ft.dropdown.Option("Nenhuma"))

    comercializadora_dd = ft.Dropdown(
        label="Comercializadora Vinculada",
        hint_text="Selecione...",
        options=trader_options,
        value=current_trader_name,
        width=380,
    )

    prestador_field = ft.TextField(
        label="Prestador de Serviço",
        hint_text="Será preenchido a partir da comercializadora",
        value=existing_data.get("service_provider") or "",
        read_only=True,
        bgcolor=ft.Colors.GREY_100,
        width=380,
    )

    def _sync_prestador(e: ft.ControlEvent) -> None:
        prestador_field.value = comercializadora_dd.value or ""
        prestador_field.update()

    comercializadora_dd.on_change = _sync_prestador

    contractor_field = ft.TextField(
        label="Contratante",
        hint_text="Nome da empresa cliente",
        value=existing_data.get("contractor") or "",
        width=380,
    )

    contract_type_dd = ft.Dropdown(
        label="Tipo de Contrato",
        hint_text="Selecione...",
        options=[
            ft.dropdown.Option("ATACADISTA"),
            ft.dropdown.Option("VAREJISTA"),
            ft.dropdown.Option("AUTOPRODUÇÃO"),
        ],
        value=existing_data.get("contract_type"),
        width=380,
    )

    contract_code_field = ft.TextField(
        label="Código do Contrato",
        hint_text="Ex: CONT-2025-001",
        value=existing_data.get("contract_code") or "",
        width=380,
    )

    start_date_field = ft.TextField(
        label="Data de Início",
        hint_text="dd/mm/aaaa",
        value=_format_date_br(existing_data.get("contract_start_date")),
        width=380,
        suffix_icon=ft.Icons.CALENDAR_MONTH,
    )

    end_date_field = ft.TextField(
        label="Data de Término",
        hint_text="dd/mm/aaaa",
        value=_format_date_br(existing_data.get("contract_end_date")),
        width=380,
        suffix_icon=ft.Icons.CALENDAR_MONTH,
    )

    # ------------------------ Campos comerciais ------------------------
    def _fmt_float(val):
        return str(val).replace('.', ',') if val is not None else ""

    fee_tax_field = ft.TextField(
        label="Taxa de Fee (R$/MWh)",
        hint_text="Ex: 2.50",
        value=_fmt_float(existing_data.get("fee_tax")),
        width=380,
    )

    energy_note_date_field = ft.TextField(
        label="Data da Nota de Energia (du)",
        hint_text="Dia de vencimento",
        value=str(existing_data.get("energy_note_date") or ""),
        width=380,
    )

    has_proinfa_cb = ft.Checkbox(
        label="Possui Desconto PROINFA",
        value=bool(existing_data.get("has_proinfa_discount")),
    )

    financial_guarantee_cb = ft.Checkbox(
        label="Garantia Financeira Ativa",
        value=False, # Campo não existe na tabela contracts, mantido como placeholder visual ou se for adicionado depois
    )

    # ------------------------ Campos técnicos ------------------------
    # Mapeamento reverso para exibir no dropdown
    energy_source_map_rev = {
        "CONVENCIONAL": "CONV",
        "I5": "I5",
        "I1": "I1",
        "CQ5": "CQ5",
    }
    es_val = existing_data.get("energy_source_type")
    energy_source_dd = ft.Dropdown(
        label="Tipo de Fonte de Energia",
        hint_text="Selecione...",
        options=[
            ft.dropdown.Option("CONV"),
            ft.dropdown.Option("I5"),
            ft.dropdown.Option("I1"),
            ft.dropdown.Option("CQ5"),
        ],
        value=energy_source_map_rev.get(es_val, es_val),
        width=380,
    )

    submarket_map_rev = {
        "SUDESTE": "SE/CO",
        "NORDESTE": "NE",
        "NORTE": "N",
        "SUL": "S",
    }
    sm_val = existing_data.get("submarket")
    submarket_dd = ft.Dropdown(
        label="Submercado",
        hint_text="Selecione...",
        options=[
            ft.dropdown.Option("SE/CO"),
            ft.dropdown.Option("NE"),
            ft.dropdown.Option("N"),
            ft.dropdown.Option("S"),
        ],
        value=submarket_map_rev.get(sm_val, sm_val),
        width=380,
    )

    power_load_factor_field = ft.TextField(
        label="Fator de Carga (%)",
        hint_text="Ex: 85.5",
        value=_fmt_float(existing_data.get("power_load_factor")),
        width=380,
    )

    flex_min_field = ft.TextField(
        label="Flex Mínima (%)",
        hint_text="Ex: -10",
        value=_fmt_float(existing_data.get("flex_min")),
        width=380,
    )

    flex_max_field = ft.TextField(
        label="Flex Máxima (%)",
        hint_text="Ex: +10",
        value=_fmt_float(existing_data.get("flex_max")),
        width=380,
    )

    seasonality_min_field = ft.TextField(
        label="Sazonalidade Mínima (%)",
        hint_text="Ex: -20",
        value=_fmt_float(existing_data.get("seasonality_min")),
        width=380,
    )

    seasonality_max_field = ft.TextField(
        label="Sazonalidade Máxima (%)",
        hint_text="Ex: +20",
        value=_fmt_float(existing_data.get("seasonality_max")),
        width=380,
    )

    looses_field = ft.TextField(
        label="Perdas Técnicas (%)",
        hint_text="Ex: 3.0",
        value=_fmt_float(existing_data.get("looses")),
        width=380,
    )

    # ------------------------ Configurações ------------------------
    is_active_switch = ft.Switch(
        label="Contrato Ativo",
        value=bool(existing_data.get("is_active", True)),
    )

    automatic_billing_switch = ft.Switch(
        label="Faturamento Automático Liberado",
        value=bool(existing_data.get("automatic_billing_released", False)),
    )

    # ------------------------ Layout em abas ------------------------
    dados_gerais_tab = ft.Container(
        padding=20,
        content=ft.Column(
            controls=[
                ft.Row(
                    controls=[comercializadora_dd, contract_code_field],
                    spacing=20,
                ),
                ft.Row(
                    controls=[contractor_field, contract_type_dd],
                    spacing=20,
                ),
                ft.Row(
                    controls=[start_date_field, end_date_field],
                    spacing=20,
                ),
            ],
            spacing=16,
            alignment=ft.MainAxisAlignment.START,
        ),
    )

    comercial_tab = ft.Container(
        padding=20,
        content=ft.Column(
            controls=[
                ft.Row(
                    controls=[fee_tax_field, energy_note_date_field],
                    spacing=20,
                ),
                ft.Text("Descontos e Benefícios", size=14, weight=ft.FontWeight.W_500),
                ft.Column(
                    controls=[has_proinfa_cb, financial_guarantee_cb],
                    spacing=8,
                ),
            ],
            spacing=16,
            alignment=ft.MainAxisAlignment.START,
        ),
    )

    tecnico_tab = ft.Container(
        padding=20,
        content=ft.Column(
            controls=[
                ft.Row(
                    controls=[energy_source_dd, submarket_dd],
                    spacing=20,
                ),
                ft.Row(
                    controls=[power_load_factor_field, looses_field],
                    spacing=20,
                ),
                ft.Row(
                    controls=[flex_min_field, flex_max_field],
                    spacing=20,
                ),
                ft.Row(
                    controls=[seasonality_min_field, seasonality_max_field],
                    spacing=20,
                ),
            ],
            spacing=16,
            alignment=ft.MainAxisAlignment.START,
        ),
    )

    config_tab = ft.Container(
        padding=20,
        content=ft.Column(
            controls=[
                is_active_switch,
                automatic_billing_switch,
            ],
            spacing=16,
            alignment=ft.MainAxisAlignment.START,
        ),
    )

    tabs = ft.Tabs(
        selected_index=0,
        animation_duration=300,
        tabs=[
            ft.Tab(text="Dados Gerais", icon=ft.Icons.DESCRIPTION, content=dados_gerais_tab),
            ft.Tab(text="Comercial", icon=ft.Icons.ATTACH_MONEY, content=comercial_tab),
            ft.Tab(text="Técnico", icon=ft.Icons.SETTINGS_INPUT_COMPONENT, content=tecnico_tab),
            ft.Tab(text="Configurações", icon=ft.Icons.SETTINGS, content=config_tab),
        ],
        expand=1,
    )

    # ------------------------ Ações ------------------------
    def _go_back() -> None:
        screen.navigation.go(
            "/comercializacao",
            params={
                "submenu": "contratos",
                "buyer": (buyer_filter or ""),
                "seller": (seller_filter or ""),
            },
        )

    def on_save(_: ft.ControlEvent) -> None:
        # Busca o ID do trader selecionado
        selected_trader_name = comercializadora_dd.value
        trader_id_to_save = None

        if selected_trader_name:
            # Procura na lista já carregada (traders_db)
            for t in traders_db:
                if t.get("name") == selected_trader_name:
                    trader_id_to_save = t.get("id")
                    break
        
        # Helper to convert to float
        def _to_float(val: str) -> Optional[float]:
            if not val:
                return None
            try:
                return float(val.replace(",", "."))
            except ValueError:
                return None

        data: Dict[str, Any] = {
            "trader_id": trader_id_to_save,
            "service_provider": prestador_field.value,
            "contractor": contractor_field.value,
            "contract_type": contract_type_dd.value,
            "contract_code": contract_code_field.value,
            "contract_start_date": _parse_date_br(start_date_field.value),
            "contract_end_date": _parse_date_br(end_date_field.value),
            "fee_tax": _to_float(fee_tax_field.value),
            "energy_note_date": energy_note_date_field.value,
            "has_proinfa_discount": has_proinfa_cb.value,
            # "financial_guarantee": financial_guarantee_cb.value, 
            "energy_source_type": {
                "CONV": "CONVENCIONAL",
                "I5": "I5",
                "I1": "I1",
                "CQ5": "CQ5",
            }.get(energy_source_dd.value, energy_source_dd.value),
            "submarket": {
                "SE/CO": "SUDESTE",
                "NE": "NORDESTE",
                "N": "NORTE",
                "S": "SUL",
            }.get(submarket_dd.value, submarket_dd.value),
            "power_load_factor": _to_float(power_load_factor_field.value),
            "flex_min": _to_float(flex_min_field.value),
            "flex_max": _to_float(flex_max_field.value),
            "seasonality_min": _to_float(seasonality_min_field.value),
            "seasonality_max": _to_float(seasonality_max_field.value),
            "looses": _to_float(looses_field.value),
            "is_active": is_active_switch.value,
            "automatic_billing_released": automatic_billing_switch.value,
        }

        print(f"[{title_text}] Dados do contrato para salvar:")
        print(data)

        try:
            if is_editing:
                update_record("contracts", contract_id, data)
                msg = "Contrato atualizado com sucesso!"
            else:
                create_record("contracts", data)
                msg = "Contrato criado com sucesso!"
            
            print(f"[{title_text}] Sucesso.")
            
            snackbar = ft.SnackBar(
                content=ft.Text(msg),
                bgcolor=ft.Colors.GREEN_600,
            )
            screen.page.overlay.append(snackbar)
            snackbar.open = True
            screen.page.update()
            
            _go_back()
        except Exception as e:
            print(f"[{title_text}] Erro ao salvar: {e}")
            
            snackbar = ft.SnackBar(
                content=ft.Text(f"Erro ao salvar: {e}"),
                bgcolor=ft.Colors.RED_600,
            )
            screen.page.overlay.append(snackbar)
            snackbar.open = True
            screen.page.update()

    def on_cancel(_: ft.ControlEvent) -> None:
        print(f"[{title_text}] Operação cancelada pelo usuário")
        _go_back()

    button_width = 170
    button_height = 40

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

    card = ft.Container(
        bgcolor=ft.Colors.WHITE,
        border_radius=10,
        padding=20,
        border=ft.border.all(1, ft.Colors.BLUE_100),
        content=ft.Column(
            controls=[
                ft.Text(
                    title_text,
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

    print(f"[{title_text}] Formulário construído, retornando card...")

    return ft.Container(
        expand=True,
        padding=20,
        bgcolor=ft.Colors.BLUE_50,
        content=card,
    )

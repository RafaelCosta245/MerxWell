from typing import Any, Dict, Optional, List
from datetime import datetime

import flet as ft
from scripts.database import read_records, create_record, delete_records

def _format_date(value: Any) -> str:
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


def _create_proposals_table(
    proposals: list[Dict[str, Any]],
    screen: Any,
    on_delete: Any, # Callback for delete action
) -> ft.Control:
    headers = [
        "Comprador",
        "Vendedor",
        "Data",
        "Status",
        "Editar",
        "Gerar",
        "Excluir",
        "Contrato",
    ]

    widths = [250, 200, 120, 80, 70, 70, 70, 80]

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

    def data_cell(content: ft.Control, width: int, row_index: int) -> ft.Control:
        bg_color = ft.Colors.WHITE if row_index % 2 == 0 else ft.Colors.GREY_50
        return ft.Container(
            content=content,
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
        icon_color: str = ft.Colors.BLACK,
    ) -> ft.Control:
        bg_color = ft.Colors.WHITE if row_index % 2 == 0 else ft.Colors.GREY_50
        return ft.Container(
            content=ft.IconButton(
                icon=icon,
                icon_color=icon_color,
                tooltip=tooltip,
                on_click=on_click,
                icon_size=20,
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
    for idx, p in enumerate(proposals):
        buyer = str(p.get("customer_name") or "-")
        seller = "-" # Placeholder
        date_str = _format_date(p.get("created_at"))
        status_val = str(p.get("status") or "PENDING")

        # Status Icon Logic
        if status_val == "ACCEPTED":
            status_icon = ft.Icon(ft.Icons.CHECK_CIRCLE, color=ft.Colors.GREEN, size=20, tooltip="Aceita")
        else:
            status_icon = ft.Icon(ft.Icons.HOURGLASS_EMPTY, color=ft.Colors.ORANGE, size=20, tooltip="Pendente")

        def make_edit_action(proposal_data):
            def handler(_):
                print(f"DEBUG: Edit clicked for proposal {proposal_data.get('id')}")
                screen.navigation.go(
                    "/comercializacao",
                    params={
                        "submenu": "propostas",
                        "propostas_view": "new",
                        "proposal_id": str(proposal_data.get("id") or ""),
                    },
                )
            return handler

        def make_generate_action(proposal_data):
            def handler(e):
                print(f"DEBUG: Generate proposal clicked for {proposal_data.get('id')}")
                
                # Loading State
                btn = e.control
                original_icon = btn.icon
                btn.icon = None
                btn.content = ft.ProgressRing(width=16, height=16, stroke_width=2, color=ft.Colors.BLUE_600)
                btn.update()

                try:
                    proposal_id = proposal_data.get("id")
                    if not proposal_id:
                        return

                    # Fetch seasonalities
                    seasonalities = read_records("proposal_seasonalities", {"proposal_id": proposal_id})
                    # Sort by year
                    seasonalities.sort(key=lambda x: x.get("year") or 0)

                    if not seasonalities:
                        raise Exception("Não há dados de sazonalidade para esta proposta.")

                    # Extract lists
                    anos = [s.get("year") for s in seasonalities]
                    curva_vol = [s.get("average_volume") or 0.0 for s in seasonalities]
                    curva_precos = [s.get("price") or 0.0 for s in seasonalities]
                    
                    # Extract single values (take from first year or default)
                    first_sazo = seasonalities[0]
                    flex_val = first_sazo.get("flex")
                    sazo_val = first_sazo.get("seasonality")

                    # Format params
                    data_hoje = datetime.now().strftime("%d/%m/%Y")
                    
                    # CNPJ formatting
                    raw_cnpj = str(proposal_data.get("customer_cnpj") or "")
                    digits = "".join(filter(str.isdigit, raw_cnpj))
                    if len(digits) == 14:
                        cnpj_fmt = f"{digits[:2]}.{digits[2:5]}.{digits[5:8]}/{digits[8:12]}-{digits[12:]}"
                    else:
                        cnpj_fmt = raw_cnpj

                    # Dates
                    inicio = _format_date(proposal_data.get("supply_start"))
                    fim = _format_date(proposal_data.get("supply_end"))

                    # Tipo Proposta
                    validade = proposal_data.get("proposal_validity") or "-"
                    tipo_proposta = f"Indicativa - Validade até {validade}"

                    # ⚠️ VALIDAÇÃO: Obter e validar pasta de saída
                    from helpers.storage import get_output_directory
                    output_dir = get_output_directory(screen.page)
                    
                    if not output_dir:
                        raise Exception(
                            "⚠️ Pasta de saída não configurada!\n\n"
                            "Por favor, vá até o Backoffice e clique em "
                            "'Alterar Pasta de Saída' para escolher onde "
                            "os arquivos serão salvos."
                        )

                    # Call generator
                    from scripts.proposal_generator import generate_proposal
                    
                    output_path = generate_proposal(
                        data_hoje=data_hoje,
                        razao_social=proposal_data.get("customer_name") or "",
                        cnpj=cnpj_fmt,
                        submercado=proposal_data.get("submarket") or "",
                        inicio=inicio,
                        fim=fim,
                        curva_vol=curva_vol,
                        curva_precos=curva_precos,
                        anos=anos,
                        tipo_energia=proposal_data.get("energy_type") or "",
                        flex=str(flex_val) if flex_val is not None else "",
                        sazo=str(sazo_val) if sazo_val is not None else "",
                        modulacao=proposal_data.get("modulation") or "",
                        pagamento=str(proposal_data.get("billing_due_day") or ""),
                        qty_meses=str(proposal_data.get("guarantee_months") or ""),
                        tipo_proposta=tipo_proposta,
                        output_dir=output_dir  # Pass external directory
                    )

                    # Show success
                    snackbar = ft.SnackBar(ft.Text(f"Proposta gerada: {output_path}"), bgcolor=ft.Colors.GREEN_600)
                    screen.page.overlay.append(snackbar)
                    snackbar.open = True
                    screen.page.update()

                except Exception as ex:
                    print(f"ERROR generating proposal: {ex}")
                    snackbar = ft.SnackBar(ft.Text(f"Erro ao gerar proposta: {ex}"), bgcolor=ft.Colors.RED_600)
                    screen.page.overlay.append(snackbar)
                    snackbar.open = True
                    screen.page.update()
                
                finally:
                    # Restore State
                    btn.content = None
                    btn.icon = original_icon
                    btn.update()

            return handler
            
        def make_contract_action(proposal_data):
            def handler(_):
                print(f"DEBUG: Generate Contract clicked for proposal {proposal_data.get('id')}")
                # Future implementation: Generate Contract PDF
            return handler

        row = ft.Row(
            controls=[
                data_cell(ft.Text(buyer, size=12, color=ft.Colors.GREY_900, text_align=ft.TextAlign.CENTER), widths[0], idx),
                data_cell(ft.Text(seller, size=12, color=ft.Colors.GREY_900, text_align=ft.TextAlign.CENTER), widths[1], idx),
                data_cell(ft.Text(date_str, size=12, color=ft.Colors.GREY_900, text_align=ft.TextAlign.CENTER), widths[2], idx),
                data_cell(status_icon, widths[3], idx),
                action_button(ft.Icons.EDIT, "Editar proposta", widths[4], idx, make_edit_action(p)),
                action_button(ft.Icons.DESCRIPTION, "Gerar proposta", widths[5], idx, make_generate_action(p)),
                action_button(ft.Icons.DELETE, "Excluir proposta", widths[6], idx, lambda _: on_delete(p)),
                action_button(ft.Icons.PICTURE_AS_PDF, "Gerar Contrato", widths[7], idx, make_contract_action(p), icon_color=ft.Colors.RED_700),
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


def create_propostas_content(screen: Any) -> ft.Control:
    """Conteúdo da aba Propostas com tabela em container e scroll."""
    
    # Container para a tabela que será atualizado
    table_container = ft.Container()

    def load_proposals(search_term: str = "", status_filter: Optional[str] = None):
        print(f"DEBUG: Loading proposals with search_term='{search_term}', status_filter='{status_filter}'")
        try:
            # Fetch all proposals (filtering in memory for partial match)
            all_proposals = read_records("proposals")
            
            filtered_proposals = all_proposals

            if search_term:
                filtered_proposals = [
                    p for p in filtered_proposals 
                    if search_term.lower() in str(p.get("customer_name", "")).lower()
                ]
            
            if status_filter:
                filtered_proposals = [
                    p for p in filtered_proposals
                    if str(p.get("status", "PENDING")) == status_filter
                ]
            
            # Sort by created_at desc
            filtered_proposals.sort(key=lambda x: x.get("created_at", ""), reverse=True)

            table_container.content = _create_proposals_table(filtered_proposals, screen, handle_delete_request)
            table_container.update()
            
        except Exception as e:
            print(f"ERROR: Failed to load proposals: {e}")
            table_container.content = ft.Text(f"Erro ao carregar propostas: {e}", color=ft.Colors.RED)
            table_container.update()

    def handle_delete_request(proposal: Dict[str, Any]):
        proposal_id = proposal.get("id")
        if not proposal_id:
            return

        def confirm_delete(e):
            try:
                # --- Deletion Process ---
                
                # 1. Validar existência
                check = read_records("proposals", {"id": proposal_id})
                if not check:
                    raise Exception("Proposta não encontrada no banco de dados.")

                # 2. Log inicial (Opcional: Logar em proposal_logs antes de deletar, caso falhe)
                # Como audit_events não existe, vamos pular o log de auditoria externa.
                try:
                    create_record("proposal_logs", {
                        "proposal_id": proposal_id,
                        "message": "Deletion process initiated"
                    })
                except:
                    pass # Se falhar o log, não impede a exclusão

                # 3. Excluir proposta (cascade remove filhos)
                delete_records("proposals", {"id": proposal_id})

                # 4. Confirmar exclusão
                check_after = read_records("proposals", {"id": proposal_id})
                if check_after:
                    raise Exception("Falha crítica: A proposta não foi excluída.")

                # 5. Log final (Removido pois audit_events não existe e proposal_logs foi deletado em cascata)

                # Sucesso
                screen.page.close(dlg)
                snackbar = ft.SnackBar(ft.Text("Proposta excluída com sucesso!"), bgcolor=ft.Colors.GREEN_600)
                screen.page.overlay.append(snackbar)
                snackbar.open = True
                screen.page.update()
                
                # Refresh table
                load_proposals(buyer_field.value)

            except Exception as ex:
                screen.page.close(dlg)
                print(f"[ERROR] Delete failed: {ex}")
                snackbar = ft.SnackBar(ft.Text(f"Erro ao excluir: {str(ex)}"), bgcolor=ft.Colors.RED_600)
                screen.page.overlay.append(snackbar)
                snackbar.open = True
                screen.page.update()

        dlg = ft.AlertDialog(
            modal=True,
            title=ft.Text("Confirmar Exclusão"),
            content=ft.Text(
                "Tem certeza que deseja excluir esta proposta?\n\n"
                "⚠ ATENÇÃO: Essa ação excluirá TODOS os dados da proposta, "
                "incluindo sazonalidades e logs.\n"
                "Essa ação é IRREVERSÍVEL.",
            ),
            actions=[
                ft.TextButton("Cancelar", on_click=lambda e: screen.page.close(dlg)),
                ft.TextButton(
                    "Excluir Definitivamente",
                    on_click=confirm_delete,
                    style=ft.ButtonStyle(color=ft.Colors.RED_600),
                ),
            ],
            actions_alignment=ft.MainAxisAlignment.END,
        )
        screen.page.open(dlg)

    buyer_field = ft.TextField(
        label="Comprador",
        prefix_icon=ft.Icons.SEARCH,
        width=260,
        on_submit=lambda e: load_proposals(e.control.value)
    )

    seller_field = ft.TextField(
        label="Vendedor",
        prefix_icon=ft.Icons.SEARCH,
        width=260,
        visible=False
    )

    def apply_filters(_: ft.ControlEvent) -> None:
        load_proposals(buyer_field.value)

    filters_row = ft.Row(
        controls=[buyer_field, seller_field],
        spacing=16,
        alignment=ft.MainAxisAlignment.START,
    )

    button_width = 170
    button_height = 40

    search_button = ft.ElevatedButton(
        text="Pesquisar",
        icon=ft.Icons.SEARCH,
        bgcolor=ft.Colors.BLUE_600,
        color=ft.Colors.WHITE,
        style=ft.ButtonStyle(
            shape=ft.RoundedRectangleBorder(radius=6),
            padding=ft.padding.symmetric(horizontal=0, vertical=0),
        ),
        width=button_width,
        height=button_height,
        on_click=apply_filters,
    )

    new_proposal_button = ft.ElevatedButton(
        text="Nova Proposta",
        icon=ft.Icons.ADD,
        bgcolor=ft.Colors.BLUE_600,
        color=ft.Colors.WHITE,
        style=ft.ButtonStyle(
            shape=ft.RoundedRectangleBorder(radius=6),
            padding=ft.padding.symmetric(horizontal=0, vertical=0),
        ),
        width=button_width,
        height=button_height,
        on_click=lambda _: screen.navigation.go(
            "/comercializacao",
            params={
                "submenu": "propostas",
                "propostas_view": "new",
            },
        ),
    )

    pending_button = ft.ElevatedButton(
        text="Pendentes",
        icon=ft.Icons.HOURGLASS_EMPTY,
        bgcolor=ft.Colors.BLUE_600,
        color=ft.Colors.WHITE,
        style=ft.ButtonStyle(
            shape=ft.RoundedRectangleBorder(radius=6),
            padding=ft.padding.symmetric(horizontal=0, vertical=0),
        ),
        width=button_width,
        height=button_height,
        on_click=lambda _: load_proposals(buyer_field.value, "PENDING"),
    )

    accepted_button = ft.ElevatedButton(
        text="Aceitas",
        icon=ft.Icons.CHECK_CIRCLE,
        bgcolor=ft.Colors.BLUE_600,
        color=ft.Colors.WHITE,
        style=ft.ButtonStyle(
            shape=ft.RoundedRectangleBorder(radius=6),
            padding=ft.padding.symmetric(horizontal=0, vertical=0),
        ),
        width=button_width,
        height=button_height,
        on_click=lambda _: load_proposals(buyer_field.value, "ACCEPTED"),
    )

    all_button = ft.ElevatedButton(
        text="Todas",
        icon=ft.Icons.LIST,
        bgcolor=ft.Colors.BLUE_600,
        color=ft.Colors.WHITE,
        style=ft.ButtonStyle(
            shape=ft.RoundedRectangleBorder(radius=6),
            padding=ft.padding.symmetric(horizontal=0, vertical=0),
        ),
        width=button_width,
        height=button_height,
        on_click=lambda _: (setattr(buyer_field, 'value', ''), load_proposals()),
    )

    actions_row = ft.Row(
        controls=[
            search_button,
            new_proposal_button,
            pending_button,
            accepted_button,
            all_button,
        ],
        spacing=12,
        alignment=ft.MainAxisAlignment.START,
    )

    # Initial Load
    try:
        initial_proposals = read_records("proposals")
        initial_proposals.sort(key=lambda x: x.get("created_at", ""), reverse=True)
        table_container.content = _create_proposals_table(initial_proposals, screen, handle_delete_request)
    except Exception as e:
        table_container.content = ft.Text(f"Erro ao carregar propostas: {e}", color=ft.Colors.RED)

    return ft.Container(
        expand=True,
        padding=20,
        content=ft.Column(
            controls=[
                ft.Text("Gerenciamento de Propostas", size=24, weight=ft.FontWeight.BOLD),
                ft.Container(height=10),
                filters_row,
                ft.Container(height=12),
                actions_row,
                ft.Container(height=16),
                ft.Row(
                    controls=[table_container],
                    scroll=ft.ScrollMode.ALWAYS,
                ),
            ],
            spacing=6,
            alignment=ft.MainAxisAlignment.START,
        ),
    )

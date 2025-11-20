from typing import Any, List, Tuple, Optional
import flet as ft
from datetime import datetime, timedelta, date
import pandas as pd
from scripts.database import read_records
from scripts.icms_novo_discount_calculator import calculate_icms_price, calculate_icms_price_star

def create_precos_content(screen: Any) -> ft.Control:
    """
    Cria o conteúdo da tela de Preços (antigo Clientes), com estrutura de dashboard.
    """
    
    # --- Funções de Dados ---
    def get_i5_ne_prices() -> List[Tuple[datetime, float]]:
        """
        Busca preços de I5 NE da SERENA nos últimos 30 dias.
        Realiza forward fill para dias faltantes.
        """
        try:
            # 1. Obter ID da SERENA
            traders = read_records("traders", filters={"name": "SERENA"})
            if not traders:
                print("Comercializadora SERENA não encontrada.")
                return []
            serena_id = traders[0]["id"]
            
            # 2. Definir intervalo de datas (últimos 30 dias)
            end_date = datetime.today().date()
            start_date = end_date - timedelta(days=29)
            
            # 3. Buscar snapshots no intervalo
            snapshots = read_records("energy_price_snapshots", filters={"trader_id": serena_id})
            
            valid_snapshots = {} # {snapshot_id: date}
            for s in snapshots:
                s_date = datetime.strptime(s["snapshot_date"], "%Y-%m-%d").date()
                if start_date <= s_date <= end_date:
                    valid_snapshots[s["id"]] = s_date
            
            if not valid_snapshots:
                return []

            # 4. Buscar preços para esses snapshots
            prices_data = []
            
            all_prices_ne = read_records("energy_prices", filters={"energy_type": "I5", "submarket": "NE"})
            
            for p in all_prices_ne:
                s_id = p["snapshot_id"]
                if s_id in valid_snapshots:
                    price_val = p["price"]
                    date_val = valid_snapshots[s_id]
                    if p["year"] == 2026:
                        prices_data.append({"date": date_val, "price": price_val})
            
            if not prices_data:
                return []
                
            # 5. Criar DataFrame e Forward Fill
            df = pd.DataFrame(prices_data)
            df = df.sort_values("date")
            df.set_index("date", inplace=True)
            
            # Criar range completo de datas
            full_range = pd.date_range(start=start_date, end=end_date)
            df = df.reindex(full_range)
            
            # Forward Fill
            df["price"] = df["price"].ffill()
            
            # Se começar com NaN (primeiros dias sem dados), pode preencher com 0 ou bfill
            df["price"] = df["price"].fillna(0)
            
            # Converter para lista de tuplas
            result = []
            for dt, row in df.iterrows():
                result.append((dt, row["price"]))
                
            return result

        except Exception as ex:
            print(f"Erro ao buscar dados do gráfico: {ex}")
            return []

    def create_i5_ne_chart() -> ft.Control:
        data = get_i5_ne_prices()
        
        if not data:
            return ft.Container(
                content=ft.Text("Sem dados para exibir (SERENA - I5 NE - 2026)", color=ft.Colors.GREY_500),
                alignment=ft.alignment.center,
                bgcolor=ft.Colors.BLUE_50,
                border_radius=8,
                expand=True,
                height=350
            )
        
        # Arredondar max_y para o próximo múltiplo de 50
        max_price = max([p for _, p in data])
        max_y = ((max_price // 50) + 1) * 50
        min_y = 0
        
        print(f"Dados do gráfico (Max: {max_price}): {[p for _, p in data]}")

        line_data = []
        bottom_axis_labels = []
        
        for i, (dt, price) in enumerate(data):
            line_data.append(
                ft.LineChartDataPoint(
                    x=i, 
                    y=price,
                    tooltip=f"{dt.strftime('%d/%m')}: R$ {price:.2f}",
                )
            )
            # Labels do eixo X a cada 5 dias
            if i % 5 == 0:
                bottom_axis_labels.append(
                    ft.ChartAxisLabel(
                        value=i,
                        label=ft.Text(dt.strftime("%d/%m"), size=10, weight=ft.FontWeight.BOLD),
                    )
                )
            
        chart = ft.LineChart(
            data_series=[
                ft.LineChartData(
                    data_points=line_data,
                    stroke_width=3,
                    color=ft.Colors.BLUE_600,
                    curved=True,
                    stroke_cap_round=True,
                    below_line_bgcolor=ft.Colors.with_opacity(0.2, ft.Colors.BLUE_600),
                )
            ],
            border=ft.border.all(1, ft.Colors.GREY_200),
            left_axis=ft.ChartAxis(
                labels_size=40,
                title=ft.Text("Preço (R$)", size=10),
                title_size=20,
                labels_interval=50,
            ),
            bottom_axis=ft.ChartAxis(
                labels=bottom_axis_labels,
                labels_size=32,
            ),
            tooltip_bgcolor=ft.Colors.BLUE_900,
            min_y=min_y,
            max_y=max_y,
            expand=True,
        )
        
        return ft.Container(
            content=ft.Column(
                controls=[
                    ft.Text("Preço I5 NE (2026) - SERENA - Últimos 30 Dias", size=14, weight=ft.FontWeight.W_600, color=ft.Colors.GREY_800),
                    ft.Container(
                        content=chart,
                        expand=True,
                        padding=10,
                    )
                ],
                spacing=10,
                expand=True,
            ),
            expand=True,
            height=350,
            padding=10,
            bgcolor=ft.Colors.WHITE,
            border_radius=8,
            border=ft.border.all(1, ft.Colors.GREY_200),
        )

    # --- 1. Cabeçalho (Título e Subtítulo) ---
    header = ft.Column(
        controls=[
            ft.Text("Preços", size=24, weight=ft.FontWeight.BOLD, color=ft.Colors.BLACK87),
            ft.Text("Gestão de preços de mercado e curvas futuras.", size=14, color=ft.Colors.GREY_600),
        ],
        spacing=4,
    )

    # --- 2. Cards de Ação (Topo) ---
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
            shadow=ft.BoxShadow(
                spread_radius=1,
                blur_radius=5,
                color=ft.Colors.BLUE_50,
                offset=ft.Offset(0, 2),
            ),
            on_click=on_click,
            ink=True if on_click else False,
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
    def get_best_prices() -> Tuple[Optional[date], List[dict]]:
        """
        Encontra o menor preço de I5 NE para cada ano (2026-2030).
        Busca retroativa a partir de hoje.
        Retorna (data_encontrada, lista_de_resultados).
        """
        try:
            current_date = datetime.today().date()
            # Limite de busca retroativa (ex: 30 dias) para evitar loop infinito
            for _ in range(30):
                # Buscar snapshots para a data
                snapshots = read_records("energy_price_snapshots", filters={"snapshot_date": current_date.isoformat()})
                
                if not snapshots:
                    current_date -= timedelta(days=1)
                    continue
                
                # Se encontrou snapshots, buscar preços
                snapshot_ids = [s["id"] for s in snapshots]
                
                # Buscar preços I5 NE para os anos 2026-2030 nesses snapshots
                # Como não temos filtro "IN", vamos buscar por tipo e submercado e filtrar em memória
                all_prices_ne = read_records("energy_prices", filters={"energy_type": "I5", "submarket": "NE"})
                
                # Filtrar pelos snapshots da data e anos desejados
                relevant_prices = [
                    p for p in all_prices_ne 
                    if p["snapshot_id"] in snapshot_ids and 2026 <= p["year"] <= 2033
                ]
                
                if not relevant_prices:
                    current_date -= timedelta(days=1)
                    continue
                
                # Encontrou preços! Agora achar o menor por ano
                results = []
                years = range(2026, 2034)
                
                # Carregar traders para pegar nomes
                all_traders = read_records("traders")
                trader_map = {t["id"]: t["name"] for t in all_traders}
                snapshot_trader_map = {s["id"]: s["trader_id"] for s in snapshots}
                
                for year in years:
                    year_prices = [p for p in relevant_prices if p["year"] == year]
                    
                    if not year_prices:
                        results.append({"year": year, "price": None, "trader": "-"})
                        continue
                        
                    # Encontrar menor preço
                    best_price_record = min(year_prices, key=lambda x: x["price"])
                    best_price = best_price_record["price"]
                    
                    # Encontrar fornecedor
                    snap_id = best_price_record["snapshot_id"]
                    trader_id = snapshot_trader_map.get(snap_id)
                    trader_name = trader_map.get(trader_id, "Desconhecido")
                    
                    results.append({
                        "year": year,
                        "price": best_price,
                        "trader": trader_name
                    })
                
                return current_date, results
            
            return None, []
            
        except Exception as ex:
            print(f"Erro ao buscar melhores preços: {ex}")
            return None, []

    def create_prices_table() -> ft.Control:
        found_date, data = get_best_prices()
        
        title_text = "Preços NOVO"
        if found_date:
            title_text = f"Preços NOVO COM {found_date.strftime('%d/%m/%Y')}"
        else:
            title_text = "Preços NOVO (Sem dados recentes)"

        if not data:
             return ft.Container(
                content=ft.Column(
                    controls=[
                        ft.Text(title_text, size=14, weight=ft.FontWeight.W_600, color=ft.Colors.GREY_800),
                        ft.Container(
                            content=ft.Text("Nenhum dado encontrado nos últimos 30 dias.", color=ft.Colors.GREY_500),
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
                height=350,
                padding=10,
            )

        # Definição de Cabeçalhos e Larguras (Estilo Contratos)
        headers = [
            "Ano",
            "Preço Base",
            "Fornecedor",
            "10% ICMS",
            "15% ICMS",
            "20% ICMS",
            "25% ICMS",
            "10% ICMS*",
            "15% ICMS*",
            "20% ICMS*",
            "25% ICMS*",
        ]
        # Ajuste as larguras conforme necessário para caber no espaço
        widths = [60, 98, 150, 98, 98, 98, 98, 98, 98, 98, 98]
        
        total_width = sum(widths)

        def header_cell(text: str, width: int) -> ft.Control:
            return ft.Container(
                content=ft.Text(
                    text,
                    size=12,
                    weight=ft.FontWeight.BOLD,
                    color=ft.Colors.WHITE,
                    text_align=ft.TextAlign.CENTER,
                ),
                width=width,
                height=40,
                bgcolor=ft.Colors.BLUE_700,
                padding=5,
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
                height=35,
                bgcolor=bg_color,
                padding=5,
                alignment=ft.alignment.center,
                border=ft.border.all(1, ft.Colors.GREY_300),
            )

        # Criar linha de cabeçalho
        header_row = ft.Row(
            controls=[header_cell(headers[i], widths[i]) for i in range(len(headers))],
            spacing=0,
        )

        # Criar linhas de dados
        data_rows = []
        for idx, row_data in enumerate(data):
            year = row_data["year"]
            price = row_data["price"]
            trader = row_data["trader"]
            
            if price is not None:
                p_base = f"R$ {price:.2f}".replace('.', ',')
                p_10 = f"R$ {calculate_icms_price(price, 0.10):.2f}".replace('.', ',')
                p_15 = f"R$ {calculate_icms_price(price, 0.15):.2f}".replace('.', ',')
                p_20 = f"R$ {calculate_icms_price(price, 0.20):.2f}".replace('.', ',')
                p_25 = f"R$ {calculate_icms_price(price, 0.25):.2f}".replace('.', ',')
                
                p_10_star = f"R$ {calculate_icms_price_star(price, 0.10):.2f}".replace('.', ',')
                p_15_star = f"R$ {calculate_icms_price_star(price, 0.15):.2f}".replace('.', ',')
                p_20_star = f"R$ {calculate_icms_price_star(price, 0.20):.2f}".replace('.', ',')
                p_25_star = f"R$ {calculate_icms_price_star(price, 0.25):.2f}".replace('.', ',')
            else:
                p_base = "-"
                p_10 = "-"
                p_15 = "-"
                p_20 = "-"
                p_25 = "-"
                p_10_star = "-"
                p_15_star = "-"
                p_20_star = "-"
                p_25_star = "-"
            
            row_controls = [
                data_cell(str(year), widths[0], idx),
                data_cell(p_base, widths[1], idx),
                data_cell(trader, widths[2], idx),
                data_cell(p_10, widths[3], idx),
                data_cell(p_15, widths[4], idx),
                data_cell(p_20, widths[5], idx),
                data_cell(p_25, widths[6], idx),
                data_cell(p_10_star, widths[7], idx),
                data_cell(p_15_star, widths[8], idx),
                data_cell(p_20_star, widths[9], idx),
                data_cell(p_25_star, widths[10], idx),
            ]
            
            data_rows.append(ft.Row(controls=row_controls, spacing=0))

        # Montar tabela final
        table_column = ft.Column(
            controls=[header_row] + data_rows,
            spacing=0,
            # scroll=ft.ScrollMode.AUTO, # Scroll vertical se necessário
        )
        
        # Container com largura total para permitir scroll horizontal
        table_container = ft.Container(
            content=table_column,
            width=total_width + 5,
            bgcolor=ft.Colors.WHITE,
            border_radius=8,
            border=ft.border.all(1, ft.Colors.GREY_200),
        )

        return ft.Container(
            content=ft.Column(
                controls=[
                    ft.Text(title_text, size=14, weight=ft.FontWeight.W_600, color=ft.Colors.GREY_800),
                    ft.Container(
                        content=ft.Row(
                            controls=[table_container],
                            scroll=ft.ScrollMode.ALWAYS,
                            expand=True
                        ),
                        expand=True,
                        padding=10
                    )
                ],
                spacing=10,
                expand=True,
            ),
            expand=True,
            height=350,
            padding=10,
        )

    charts_section = ft.Container(
        content=ft.Column(
            controls=[
                ft.Text("Preços Médios de Energia", size=18, weight=ft.FontWeight.BOLD, color=ft.Colors.BLACK87),
                ft.Column(
                    controls=[
                        create_prices_table(),
                        create_i5_ne_chart(),
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
        height=900,
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

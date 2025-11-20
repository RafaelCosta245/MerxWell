# ======================================================================================
# MERXWELL - T2: EXPOSIÇÃO AO MCP (CORRIGIDO)
# Compatível com sua versão do Flet
# ======================================================================================

import flet as ft

# ------------------------------------------------------------------------------
# MOCKS (você vai substituir depois por dados reais do Supabase)
# ------------------------------------------------------------------------------

MESES = [
	"JAN", "FEV", "MAR", "ABR", "MAI", "JUN",
	"JUL", "AGO", "SET", "OUT", "NOV", "DEZ"
]

EXPOSICAO_MWH = {
	"JAN": -120, "FEV": -80, "MAR": 40, "ABR": 90,
	"MAI": 150, "JUN": 210, "JUL": 170, "AGO": 130,
	"SET": -30, "OUT": -60, "NOV": 10, "DEZ": 50,
}

PLD_MEDIO_5Y = {
	"JAN": 140, "FEV": 130, "MAR": 135, "ABR": 150,
	"MAI": 160, "JUN": 170, "JUL": 180, "AGO": 190,
	"SET": 175, "OUT": 165, "NOV": 150, "DEZ": 145,
}

PLD_MIN = {m: 60 for m in MESES}
PLD_MAX = {m: 500 for m in MESES}


# ------------------------------------------------------------------------------
# Funções de cálculo
# ------------------------------------------------------------------------------

def calcular_exposicao_financeira(pld_por_mes: dict[str, float]):
	return {mes: EXPOSICAO_MWH[mes] * pld_por_mes[mes] for mes in MESES}


def somatorio(d: dict[str, float]):
	return sum(d.values())


# ------------------------------------------------------------------------------
# APLICAÇÃO PRINCIPAL
# ------------------------------------------------------------------------------

def main(page: ft.Page):
	page.title = "MERX Energia – Exposição ao MCP"
	page.theme_mode = ft.ThemeMode.LIGHT
	page.bgcolor = ft.Colors.BLUE_GREY_50
	page.padding = 20
	page.scroll = ft.ScrollMode.AUTO

	# Estado: PLD simulado
	pld_simulado = {m: PLD_MEDIO_5Y[m] for m in MESES}

	# Cálculo inicial
	risco_min = calcular_exposicao_financeira(PLD_MIN)
	risco_med = calcular_exposicao_financeira(PLD_MEDIO_5Y)
	risco_max = calcular_exposicao_financeira(PLD_MAX)

	# Refs
	risco_sim_refs = {m: ft.Ref[ft.Text]() for m in MESES}

	# Refs para Tabela de Hedge
	compra_vol_refs = {m: ft.Ref[ft.Text]() for m in MESES}
	compra_price_refs = {m: ft.Ref[ft.Text]() for m in MESES}
	venda_vol_refs = {m: ft.Ref[ft.Text]() for m in MESES}
	venda_price_refs = {m: ft.Ref[ft.Text]() for m in MESES}

	resumo_anual_ref = ft.Ref[ft.Text]()

	# ------------------------------------------------------------------------------
	# Atualização geral
	# ------------------------------------------------------------------------------

	def atualizar_interface():
		risco_sim = calcular_exposicao_financeira(pld_simulado)

		# Linha de exposição simulada na tabela
		for mes in MESES:
			risco_sim_refs[mes].current.value = f"{risco_sim[mes]:,.2f}"

		# Resumo anual
		resumo_anual_ref.current.value = (
			f"Exposição Anual (R$):  "
			f"Min: {somatorio(risco_min):,.2f} | "
			f"Médio 5a: {somatorio(risco_med):,.2f} | "
			f"Máx: {somatorio(risco_max):,.2f} | "
			f"Sim: {somatorio(risco_sim):,.2f}"
		)

		# Hedge
		montar_hedge()

		page.update()

	# ------------------------------------------------------------------------------
	# Eventos de alteração de PLD
	# ------------------------------------------------------------------------------

	def on_pld_change(mes):
		def handler(e):
			try:
				valor = float(e.control.value.replace("R$", "").replace(",", "."))
			except:
				valor = pld_simulado[mes]
				e.control.value = f"{valor:.2f}"

			pld_simulado[mes] = valor
			atualizar_interface()

		return handler

	# ------------------------------------------------------------------------------
	# GRÁFICO MWh
	# ------------------------------------------------------------------------------

	def grafico_exposicao_mwh():
		pontos = [
			ft.LineChartDataPoint(i, EXPOSICAO_MWH[MESES[i]])
			for i in range(12)
		]

		chart = ft.LineChart(
			data_series=[ft.LineChartData(data_points=pontos, color=ft.Colors.BLUE, stroke_width=3)],
			min_x=0,
			max_x=11,
			min_y=min(EXPOSICAO_MWH.values()) - 50,
			max_y=max(EXPOSICAO_MWH.values()) + 50,
			height=280,
			expand=True,
		)

		eixo_x = ft.Row(
			[ft.Text(m, width=40, text_align=ft.TextAlign.CENTER) for m in MESES],
			alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
		)

		return ft.Container(
			bgcolor=ft.Colors.WHITE,
			border_radius=12,
			padding=20,
			content=ft.Column([
				ft.Text("Exposição em Energia (MWh)", size=18, weight=ft.FontWeight.BOLD),
				ft.Text("Compras – Vendas por mês.", size=12, color=ft.Colors.GREY_600),
				ft.Container(height=10),
				ft.Text("Eixo Y: MWh", size=11, color=ft.Colors.GREY_700),
				chart,
				eixo_x,
			], spacing=6),
		)

	# ------------------------------------------------------------------------------
	# TABELA DE PLD + EXPOSIÇÃO
	# ------------------------------------------------------------------------------

	def tabela_pld_exposicao():
		rows = []
		for mes in MESES:
			campo = ft.TextField(
				value=f"{pld_simulado[mes]:.2f}",
				width=90,
				on_change=on_pld_change(mes),
				text_align=ft.TextAlign.RIGHT,
			)
			rows.append(
				ft.DataRow(
					[
						ft.DataCell(ft.Text(mes)),
						ft.DataCell(ft.Text(EXPOSICAO_MWH[mes])),
						ft.DataCell(ft.Text(PLD_MEDIO_5Y[mes])),
						ft.DataCell(ft.Text(PLD_MIN[mes])),
						ft.DataCell(ft.Text(PLD_MAX[mes])),
						ft.DataCell(campo),
						ft.DataCell(ft.Text(f"{risco_med[mes]:,.2f}")),
						ft.DataCell(ft.Text(f"{risco_min[mes]:,.2f}")),
						ft.DataCell(ft.Text(f"{risco_max[mes]:,.2f}")),
						ft.DataCell(ft.Text("0", ref=risco_sim_refs[mes])),
					]
				)
			)

		header = [
			ft.DataColumn(ft.Text("Mês")),
			ft.DataColumn(ft.Text("MWh")),
			ft.DataColumn(ft.Text("PLD 5a")),
			ft.DataColumn(ft.Text("Min")),
			ft.DataColumn(ft.Text("Máx")),
			ft.DataColumn(ft.Text("PLD Sim")),
			ft.DataColumn(ft.Text("Exp 5a")),
			ft.DataColumn(ft.Text("Exp Min")),
			ft.DataColumn(ft.Text("Exp Máx")),
			ft.DataColumn(ft.Text("Exp Sim")),
		]

		return ft.Container(
			bgcolor=ft.Colors.WHITE,
			border_radius=12,
			padding=20,
			content=ft.Column([
				ft.Text("Simulação de PLD e Exposição Financeira", size=18, weight=ft.FontWeight.BOLD),
				ft.Text("Altere o PLD do mês para recalcular a exposição.", size=12, color=ft.Colors.GREY_600),
				ft.Container(height=10),
				ft.DataTable(columns=header, rows=rows),
				ft.Container(height=10),
				ft.Text("", ref=resumo_anual_ref, size=13, color=ft.Colors.GREY_700),
			], spacing=10),
		)

	# ------------------------------------------------------------------------------
	# GRÁFICO FINANCEIRO
	# ------------------------------------------------------------------------------

	# ------------------------------------------------------------------------------
	# TABELA DE HEDGE (CUSTOMIZADA)
	# ------------------------------------------------------------------------------

	def montar_hedge():
		for mes in MESES:
			expo = EXPOSICAO_MWH[mes]
			pld = pld_simulado[mes]

			# COMPRA: expo < 0
			if expo < 0:
				vol = f"{-expo}"
				preco = f"R$ {pld:,.2f}"
				v_vol = "-"
				v_preco = "-"
			# VENDA: expo > 0
			elif expo > 0:
				vol = "-"
				preco = "-"
				v_vol = f"{expo}"
				v_preco = f"R$ {pld:,.2f}"
			else:
				vol = "-"
				preco = "-"
				v_vol = "-"
				v_preco = "-"

			if compra_vol_refs[mes].current:
				compra_vol_refs[mes].current.value = vol
				compra_price_refs[mes].current.value = preco
				venda_vol_refs[mes].current.value = v_vol
				venda_price_refs[mes].current.value = v_preco

	def tabela_hedge():
		# Styles
		header_bg = ft.Colors.BLUE_GREY_100
		row_bg = ft.Colors.WHITE
		border_color = ft.Colors.GREY_300

		def cell(content, width, bg=row_bg, bold=False):
			return ft.Container(
				content=ft.Text(content, weight=ft.FontWeight.BOLD if bold else ft.FontWeight.NORMAL, size=12,
								text_align=ft.TextAlign.CENTER),
				width=width,
				height=30,
				bgcolor=bg,
				border=ft.border.all(1, border_color),
				alignment=ft.alignment.center,
			)

		def ref_cell(ref, width, bg=row_bg):
			return ft.Container(
				content=ft.Text("-", ref=ref, size=12, text_align=ft.TextAlign.CENTER),
				width=width,
				height=30,
				bgcolor=bg,
				border=ft.border.all(1, border_color),
				alignment=ft.alignment.center,
			)

		# Row 1: Months
		row1_controls = [cell("", 100, bg=ft.Colors.TRANSPARENT)]  # Corner
		for mes in MESES:
			row1_controls.append(cell(mes, 180, bg=header_bg, bold=True))  # Spans 2 cols (80+100)

		# Row 2: Vol / Price
		row2_controls = [cell("", 100, bg=ft.Colors.TRANSPARENT)]
		for _ in MESES:
			row2_controls.append(cell("Vol.", 80, bg=header_bg))
			row2_controls.append(cell("Preço", 100, bg=header_bg))

		# Row 3: Compra
		row3_controls = [cell("Compra", 100, bg=header_bg, bold=True)]
		for mes in MESES:
			row3_controls.append(ref_cell(compra_vol_refs[mes], 80))
			row3_controls.append(ref_cell(compra_price_refs[mes], 100))

		# Row 4: Venda
		row4_controls = [cell("Venda", 100, bg=header_bg, bold=True)]
		for mes in MESES:
			row4_controls.append(ref_cell(venda_vol_refs[mes], 80))
			row4_controls.append(ref_cell(venda_price_refs[mes], 100))

		tabela_container = ft.Column(
			controls=[
				ft.Row(row1_controls, spacing=0),
				ft.Row(row2_controls, spacing=0),
				ft.Row(row3_controls, spacing=0),
				ft.Row(row4_controls, spacing=0),
			],
			spacing=0,
		)

		return ft.Container(
			bgcolor=ft.Colors.WHITE,
			border_radius=12,
			padding=20,
			content=ft.Column([
				ft.Text("Sugestões de Hedge", size=18, weight=ft.FontWeight.BOLD),
				ft.Text(
					"Para neutralizar: comprar abaixo do preço alvo; vender acima do preço alvo.",
					size=12,
					color=ft.Colors.GREY_600,
				),
				ft.Container(height=10),
				ft.Row(
					controls=[tabela_container],
					scroll=ft.ScrollMode.AUTO,
				),
			], spacing=10),
		)

	# ------------------------------------------------------------------------------
	# Construção final da página
	# ------------------------------------------------------------------------------

	page.add(
		ft.Text("Comercialização › Exposição ao MCP", size=22, weight=ft.FontWeight.BOLD),
		ft.Container(height=10),
		grafico_exposicao_mwh(),
		ft.Container(height=20),
		tabela_pld_exposicao(),
		ft.Container(height=20),
		tabela_hedge(),
	)

	atualizar_interface()


# ------------------------------------------------------------------------------
# RUN
# ------------------------------------------------------------------------------
if __name__ == "__main__":
	ft.app(target=main)

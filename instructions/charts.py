import flet as ft


def main(page: ft.Page):
	page.title = "Gráfico de Barras Duplas"
	page.padding = 30
	page.scroll = "auto"

	# Dados de exemplo: Vendas e Meta por mês
	meses = ["Jan", "Fev", "Mar", "Abr", "Mai", "Jun"]
	vendas = [120, 150, 130, 180, 160, 190]
	metas = [100, 140, 150, 170, 165, 185]

	# Criando o gráfico de barras duplas
	bar_chart = ft.BarChart(
		bar_groups=[
			ft.BarChartGroup(
				x=i,
				bar_rods=[
					# Primeira barra (Vendas)
					ft.BarChartRod(
						from_y=0,
						to_y=vendas[i],
						width=15,
						color=ft.Colors.BLUE_400,
						tooltip=f"Vendas: {vendas[i]}",
						border_radius=5,
					),
					# Segunda barra (Meta)
					ft.BarChartRod(
						from_y=0,
						to_y=metas[i],
						width=15,
						color=ft.Colors.ORANGE_400,
						tooltip=f"Meta: {metas[i]}",
						border_radius=5,
					),
				],
				group_vertically=False,  # Barras lado a lado
			) for i in range(len(meses))
		],
		border=ft.border.all(2, ft.Colors.GREY_400),
		left_axis=ft.ChartAxis(
			labels_size=45,
			title=ft.Text("Valores (mil)", size=14, weight=ft.FontWeight.BOLD),
			title_size=40,
		),
		bottom_axis=ft.ChartAxis(
			labels_size=32,
			labels=[
				ft.ChartAxisLabel(value=i, label=ft.Text(meses[i], size=12, weight=ft.FontWeight.BOLD))
				for i in range(len(meses))
			],
		),
		horizontal_grid_lines=ft.ChartGridLines(
			interval=25,
			color=ft.Colors.GREY_300,
			width=1
		),
		tooltip_bgcolor=ft.Colors.with_opacity(0.9, ft.Colors.GREY_800),
		max_y=200,
		min_y=0,
		expand=True,
	)

	# Layout da página
	page.add(
		ft.Container(
			content=ft.Column([
				ft.Text(
					"📊 Gráfico de Barras Duplas",
					size=32,
					weight=ft.FontWeight.BOLD,
					text_align=ft.TextAlign.CENTER,
				),
				ft.Text(
					"Comparação: Vendas vs Meta Mensal",
					size=18,
					color=ft.Colors.GREY_700,
					text_align=ft.TextAlign.CENTER,
				),

				# Legenda
				ft.Row([
					ft.Container(
						content=ft.Row([
							ft.Container(
								width=20,
								height=20,
								bgcolor=ft.Colors.BLUE_400,
								border_radius=5,
							),
							ft.Text("Vendas", size=16, weight=ft.FontWeight.W_500),
						], spacing=10),
						padding=10,
					),
					ft.Container(
						content=ft.Row([
							ft.Container(
								width=20,
								height=20,
								bgcolor=ft.Colors.ORANGE_400,
								border_radius=5,
							),
							ft.Text("Meta", size=16, weight=ft.FontWeight.W_500),
						], spacing=10),
						padding=10,
					),
				], alignment=ft.MainAxisAlignment.CENTER),

				# Gráfico
				ft.Container(
					content=bar_chart,
					height=450,
					padding=20,
					border=ft.border.all(2, ft.Colors.BLUE_200),
					border_radius=10,
					bgcolor=ft.Colors.WHITE,
				),

				# Informações adicionais
				ft.Divider(height=20, thickness=2),

				ft.Text("💡 Recursos do Gráfico:", size=20, weight=ft.FontWeight.BOLD),
				ft.Column([
					ft.Row([
						ft.Icon(ft.Icons.CHECK_CIRCLE, color=ft.Colors.GREEN, size=20),
						ft.Text("Duas barras por categoria (mês)", size=14),
					]),
					ft.Row([
						ft.Icon(ft.Icons.CHECK_CIRCLE, color=ft.Colors.GREEN, size=20),
						ft.Text("Tooltips informativos ao passar o mouse", size=14),
					]),
					ft.Row([
						ft.Icon(ft.Icons.CHECK_CIRCLE, color=ft.Colors.GREEN, size=20),
						ft.Text("Cores diferenciadas para cada série", size=14),
					]),
					ft.Row([
						ft.Icon(ft.Icons.CHECK_CIRCLE, color=ft.Colors.GREEN, size=20),
						ft.Text("Grade horizontal para facilitar leitura", size=14),
					]),
				], spacing=10),

			], spacing=20, horizontal_alignment=ft.CrossAxisAlignment.CENTER),
			padding=20,
		)
	)


ft.app(target=main)
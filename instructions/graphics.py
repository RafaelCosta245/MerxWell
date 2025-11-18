import flet as ft
import math


def main(page: ft.Page):
	page.title = "Gráficos Nativos do Flet"
	page.scroll = "auto"
	page.padding = 20

	# LineChart - Gráfico de Linha
	line_chart = ft.LineChart(
		data_series=[
			ft.LineChartData(
				data_points=[
					ft.LineChartDataPoint(0, 1),
					ft.LineChartDataPoint(1, 3),
					ft.LineChartDataPoint(2, 2),
					ft.LineChartDataPoint(3, 5),
					ft.LineChartDataPoint(4, 3),
					ft.LineChartDataPoint(5, 4),
				],
				stroke_width=4,
				color=ft.Colors.BLUE,
				curved=True,
				stroke_cap_round=True,
			),
			ft.LineChartData(
				data_points=[
					ft.LineChartDataPoint(0, 2),
					ft.LineChartDataPoint(1, 1),
					ft.LineChartDataPoint(2, 4),
					ft.LineChartDataPoint(3, 2),
					ft.LineChartDataPoint(4, 5),
					ft.LineChartDataPoint(5, 3),
				],
				stroke_width=4,
				color=ft.Colors.RED,
				curved=True,
				stroke_cap_round=True,
			),
		],
		border=ft.border.all(1, ft.Colors.with_opacity(0.2, ft.Colors.ON_SURFACE)),
		horizontal_grid_lines=ft.ChartGridLines(
			interval=1, color=ft.Colors.with_opacity(0.2, ft.Colors.ON_SURFACE), width=1
		),
		vertical_grid_lines=ft.ChartGridLines(
			interval=1, color=ft.Colors.with_opacity(0.2, ft.Colors.ON_SURFACE), width=1
		),
		left_axis=ft.ChartAxis(
			labels_size=40,
		),
		bottom_axis=ft.ChartAxis(
			labels_size=40,
		),
		tooltip_bgcolor=ft.Colors.with_opacity(0.8, ft.Colors.BLUE_GREY),
		min_y=0,
		max_y=6,
		min_x=0,
		max_x=5,
		expand=True,
	)

	# BarChart - Gráfico de Barras
	bar_chart = ft.BarChart(
		bar_groups=[
			ft.BarChartGroup(
				x=0,
				bar_rods=[
					ft.BarChartRod(
						from_y=0,
						to_y=40,
						width=40,
						color=ft.Colors.AMBER,
						tooltip="Janeiro",
						border_radius=5,
					),
				],
			),
			ft.BarChartGroup(
				x=1,
				bar_rods=[
					ft.BarChartRod(
						from_y=0,
						to_y=100,
						width=40,
						color=ft.Colors.BLUE,
						tooltip="Fevereiro",
						border_radius=5,
					),
				],
			),
			ft.BarChartGroup(
				x=2,
				bar_rods=[
					ft.BarChartRod(
						from_y=0,
						to_y=70,
						width=40,
						color=ft.Colors.GREEN,
						tooltip="Março",
						border_radius=5,
					),
				],
			),
			ft.BarChartGroup(
				x=3,
				bar_rods=[
					ft.BarChartRod(
						from_y=0,
						to_y=120,
						width=40,
						color=ft.Colors.ORANGE,
						tooltip="Abril",
						border_radius=5,
					),
				],
			),
			ft.BarChartGroup(
				x=4,
				bar_rods=[
					ft.BarChartRod(
						from_y=0,
						to_y=90,
						width=40,
						color=ft.Colors.PURPLE,
						tooltip="Maio",
						border_radius=5,
					),
				],
			),
		],
		border=ft.border.all(1, ft.Colors.GREY_400),
		left_axis=ft.ChartAxis(
			labels_size=40,
		),
		bottom_axis=ft.ChartAxis(
			labels_size=30,
		),
		horizontal_grid_lines=ft.ChartGridLines(
			interval=20, color=ft.Colors.GREY_300, width=1
		),
		tooltip_bgcolor=ft.Colors.with_opacity(0.8, ft.Colors.GREY_300),
		max_y=140,
		expand=True,
	)

	# PieChart - Gráfico de Pizza
	pie_chart = ft.PieChart(
		sections=[
			ft.PieChartSection(
				value=25,
				title="25%",
				color=ft.Colors.BLUE,
				radius=100,
				title_style=ft.TextStyle(
					size=16,
					color=ft.Colors.WHITE,
					weight=ft.FontWeight.BOLD,
				),
			),
			ft.PieChartSection(
				value=35,
				title="35%",
				color=ft.Colors.RED,
				radius=110,
				title_style=ft.TextStyle(
					size=16,
					color=ft.Colors.WHITE,
					weight=ft.FontWeight.BOLD,
				),
			),
			ft.PieChartSection(
				value=20,
				title="20%",
				color=ft.Colors.GREEN,
				radius=100,
				title_style=ft.TextStyle(
					size=16,
					color=ft.Colors.WHITE,
					weight=ft.FontWeight.BOLD,
				),
			),
			ft.PieChartSection(
				value=20,
				title="20%",
				color=ft.Colors.AMBER,
				radius=100,
				title_style=ft.TextStyle(
					size=16,
					color=ft.Colors.WHITE,
					weight=ft.FontWeight.BOLD,
				),
			),
		],
		sections_space=2,
		center_space_radius=0,
		expand=True,
	)

	# Layout da página
	page.add(
		ft.Text("Gráficos Nativos do Flet", size=30, weight=ft.FontWeight.BOLD),
		ft.Divider(),

		# LineChart
		ft.Container(
			content=ft.Column([
				ft.Text("1. LineChart - Gráfico de Linha", size=20, weight=ft.FontWeight.BOLD),
				ft.Container(
					content=line_chart,
					height=300,
					padding=10,
				),
			]),
			margin=ft.margin.only(bottom=20),
		),

		# BarChart
		ft.Container(
			content=ft.Column([
				ft.Text("2. BarChart - Gráfico de Barras", size=20, weight=ft.FontWeight.BOLD),
				ft.Container(
					content=bar_chart,
					height=300,
					padding=10,
				),
			]),
			margin=ft.margin.only(bottom=20),
		),

		# PieChart
		ft.Container(
			content=ft.Column([
				ft.Text("3. PieChart - Gráfico de Pizza", size=20, weight=ft.FontWeight.BOLD),
				ft.Container(
					content=pie_chart,
					height=300,
					padding=10,
				),
			]),
			margin=ft.margin.only(bottom=20),
		),
	)


ft.app(target=main)
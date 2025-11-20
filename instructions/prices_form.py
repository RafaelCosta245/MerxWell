import flet as ft
from typing import Optional, Callable, Any
import pandas as pd
from datetime import datetime


# ============================================
# CLASSE DO DIALOG
# ============================================

class NovaCurvaDialog:
	"""Dialog para cadastro de nova curva de preços"""

	def __init__(self, page: ft.Page, on_save: Optional[Callable] = None):
		self.page = page
		self.on_save = on_save
		self.dados_precos = {}

	def show(self):
		"""Abre o dialog de seleção de modo"""

		def on_modo_manual(e):
			self.page.close(selection_dialog)
			self._open_manual_form()

		def on_modo_arquivo(e):
			self.page.close(selection_dialog)
			self._open_file_picker()

		selection_dialog = ft.AlertDialog(
			modal=True,
			title=ft.Text("Nova Curva de Preços", size=20, weight=ft.FontWeight.BOLD),
			content=ft.Container(
				content=ft.Column(
					controls=[
						ft.Text(
							"Escolha como deseja cadastrar a nova curva:",
							size=14,
							color=ft.Colors.GREY_700,
						),
						ft.Container(height=20),

						# Card: Entrada Manual
						ft.Container(
							content=ft.Column(
								controls=[
									ft.Icon(ft.Icons.EDIT_NOTE, size=48, color=ft.Colors.BLUE_600),
									ft.Text("Entrada Manual", size=16, weight=ft.FontWeight.BOLD),
									ft.Text(
										"Preencha os preços ano a ano",
										size=12,
										color=ft.Colors.GREY_600,
										text_align=ft.TextAlign.CENTER,
									),
									ft.Container(height=10),
									ft.ElevatedButton(
										text="Selecionar",
										bgcolor=ft.Colors.BLUE_700,
										color=ft.Colors.WHITE,
										on_click=on_modo_manual,
									),
								],
								horizontal_alignment=ft.CrossAxisAlignment.CENTER,
								spacing=10,
							),
							width=200,
							padding=20,
							border=ft.border.all(2, ft.Colors.BLUE_200),
							border_radius=12,
							bgcolor=ft.Colors.BLUE_50,
						),

						ft.Container(height=20),
						ft.Divider(height=1, color=ft.Colors.GREY_300),
						ft.Container(height=20),

						# Card: Importar Planilha
						ft.Container(
							content=ft.Column(
								controls=[
									ft.Icon(ft.Icons.UPLOAD_FILE, size=48, color=ft.Colors.GREEN_600),
									ft.Text("Importar Planilha", size=16, weight=ft.FontWeight.BOLD),
									ft.Text(
										"Carregue um arquivo Excel",
										size=12,
										color=ft.Colors.GREY_600,
										text_align=ft.TextAlign.CENTER,
									),
									ft.Container(height=10),
									ft.ElevatedButton(
										text="Selecionar",
										bgcolor=ft.Colors.GREEN_700,
										color=ft.Colors.WHITE,
										on_click=on_modo_arquivo,
									),
								],
								horizontal_alignment=ft.CrossAxisAlignment.CENTER,
								spacing=10,
							),
							width=200,
							padding=20,
							border=ft.border.all(2, ft.Colors.GREEN_200),
							border_radius=12,
							bgcolor=ft.Colors.GREEN_50,
						),
					],
					horizontal_alignment=ft.CrossAxisAlignment.CENTER,
					spacing=10,
				),
				width=500,
			),
			actions=[
				ft.TextButton("Cancelar", on_click=lambda e: self.page.close(selection_dialog)),
			],
			actions_alignment=ft.MainAxisAlignment.END,
		)

		self.page.open(selection_dialog)

	def _open_file_picker(self):
		"""Abre o seletor de arquivos"""

		def on_file_result(e: ft.FilePickerResultEvent):
			if e.files and len(e.files) > 0:
				file_path = e.files[0].path
				self._process_excel_file(file_path)

		file_picker = ft.FilePicker(on_result=on_file_result)
		self.page.overlay.append(file_picker)
		self.page.update()

		file_picker.pick_files(
			dialog_title="Selecione a planilha de preços",
			allowed_extensions=["xlsx", "xls"],
			file_type=ft.FilePickerFileType.CUSTOM,
		)

	def _process_excel_file(self, file_path: str):
		"""Processa o arquivo Excel"""
		try:
			df = pd.read_excel(file_path)
			precos = {}

			for col in df.columns:
				if col == "PRODUTO":
					continue

				submercado, tipo = col.split("_")

				if tipo not in precos:
					precos[tipo] = {}

				if submercado not in precos[tipo]:
					precos[tipo][submercado] = {}

				for _, row in df.iterrows():
					ano = int(row["PRODUTO"])
					preco = float(row[col])
					precos[tipo][submercado][ano] = preco

			self.dados_precos = precos
			self._show_preview_dialog()

		except Exception as ex:
			self._show_error_dialog(f"Erro ao processar arquivo: {str(ex)}")

	def _show_preview_dialog(self):
		"""Mostra preview dos dados carregados"""

		total_registros = 0
		tipos = list(self.dados_precos.keys())
		submercados = set()
		anos = set()

		for tipo, subs in self.dados_precos.items():
			for sub, anos_dict in subs.items():
				submercados.add(sub)
				for ano in anos_dict.keys():
					anos.add(ano)
					total_registros += 1

		preview_content = ft.Column(
			controls=[
				ft.Text("Dados Carregados com Sucesso!", size=16, weight=ft.FontWeight.BOLD, color=ft.Colors.GREEN_700),
				ft.Divider(height=20),
				ft.Text(f"📊 Total de registros: {total_registros}", size=14),
				ft.Text(f"⚡ Tipos de energia: {', '.join(tipos)}", size=14),
				ft.Text(f"📍 Submercados: {', '.join(sorted(submercados))}", size=14),
				ft.Text(f"📅 Anos: {min(anos)} a {max(anos)}", size=14),
			],
			spacing=10,
		)

		def on_confirmar(e):
			self.page.close(preview_dialog)
			if self.on_save:
				self.on_save(self.dados_precos, 'arquivo')
			self._show_success_message()

		preview_dialog = ft.AlertDialog(
			modal=True,
			title=ft.Text("Preview dos Dados"),
			content=ft.Container(content=preview_content, width=400),
			actions=[
				ft.TextButton("Cancelar", on_click=lambda e: self.page.close(preview_dialog)),
				ft.ElevatedButton(
					text="Confirmar e Salvar",
					bgcolor=ft.Colors.GREEN_700,
					color=ft.Colors.WHITE,
					on_click=on_confirmar,
				),
			],
		)

		self.page.open(preview_dialog)

	def _open_manual_form(self):
		"""Abre o formulário de entrada manual"""

		trader_dropdown = ft.Dropdown(
			label="Comercializadora",
			hint_text="Selecione",
			options=[
				ft.dropdown.Option("trader-1", "Comercializadora A"),
				ft.dropdown.Option("trader-2", "Comercializadora B"),
			],
			width=300,
		)

		tipo_energia_dropdown = ft.Dropdown(
			label="Tipo de Energia",
			options=[
				ft.dropdown.Option("I5", "I5 - Incentivada 50%"),
				ft.dropdown.Option("I1", "I1 - Incentivada 100%"),
				ft.dropdown.Option("CQ5", "CQ5 - Convencional Qualificada"),
				ft.dropdown.Option("CONVENCIONAL", "Convencional"),
			],
			width=300,
		)

		submercado_dropdown = ft.Dropdown(
			label="Submercado",
			options=[
				ft.dropdown.Option("NORDESTE", "Nordeste"),
				ft.dropdown.Option("NORTE", "Norte"),
				ft.dropdown.Option("SUL", "Sul"),
				ft.dropdown.Option("SUDESTE", "Sudeste"),
			],
			width=300,
		)

		anos_fields = ft.Column(spacing=10, scroll=ft.ScrollMode.AUTO, height=250)

		def adicionar_ano():
			ano_atual = datetime.now().year

			row = ft.Row(
				controls=[
					ft.TextField(
						label="Ano",
						value=str(ano_atual),
						width=100,
						keyboard_type=ft.KeyboardType.NUMBER,
					),
					ft.TextField(
						label="Preço (R$)",
						hint_text="150.50",
						width=150,
						keyboard_type=ft.KeyboardType.NUMBER,
					),
					ft.IconButton(
						icon=ft.Icons.DELETE,
						icon_color=ft.Colors.RED_600,
						on_click=lambda e, r=row: (anos_fields.controls.remove(r), self.page.update()),
					),
				],
				spacing=10,
			)
			anos_fields.controls.append(row)
			self.page.update()

		adicionar_ano()

		def validar_e_salvar(e):
			if not trader_dropdown.value or not tipo_energia_dropdown.value or not submercado_dropdown.value:
				self._show_error_dialog("Preencha todos os campos obrigatórios")
				return

			if len(anos_fields.controls) == 0:
				self._show_error_dialog("Adicione pelo menos um ano/preço")
				return

			precos_manual = {
				tipo_energia_dropdown.value: {
					submercado_dropdown.value: {}
				}
			}

			try:
				for row in anos_fields.controls:
					ano = int(row.controls[0].value)
					preco = float(row.controls[1].value.replace(",", "."))
					precos_manual[tipo_energia_dropdown.value][submercado_dropdown.value][ano] = preco

				self.page.close(form_dialog)

				if self.on_save:
					self.on_save(precos_manual, 'manual', trader_dropdown.value)

				self._show_success_message()

			except (ValueError, AttributeError) as ex:
				self._show_error_dialog(f"Erro: {str(ex)}")

		form_content = ft.Column(
			controls=[
				ft.Text("Informações Gerais", size=16, weight=ft.FontWeight.BOLD),
				trader_dropdown,
				tipo_energia_dropdown,
				submercado_dropdown,
				ft.Divider(),
				ft.Text("Preços por Ano", size=16, weight=ft.FontWeight.BOLD),
				anos_fields,
				ft.ElevatedButton(
					text="+ Adicionar Ano",
					icon=ft.Icons.ADD,
					on_click=lambda e: adicionar_ano(),
				),
			],
			spacing=15,
			scroll=ft.ScrollMode.AUTO,
		)

		form_dialog = ft.AlertDialog(
			modal=True,
			title=ft.Text("Cadastro Manual"),
			content=ft.Container(content=form_content, width=450, height=550),
			actions=[
				ft.TextButton("Cancelar", on_click=lambda e: self.page.close(form_dialog)),
				ft.ElevatedButton(
					text="Salvar",
					bgcolor=ft.Colors.GREEN_700,
					color=ft.Colors.WHITE,
					on_click=validar_e_salvar,
				),
			],
		)

		self.page.open(form_dialog)

	def _show_error_dialog(self, message: str):
		error_dialog = ft.AlertDialog(
			modal=True,
			title=ft.Text("Erro", color=ft.Colors.RED_600),
			content=ft.Text(message),
			actions=[ft.TextButton("OK", on_click=lambda e: self.page.close(error_dialog))],
		)
		self.page.open(error_dialog)

	def _show_success_message(self):
		success_dialog = ft.AlertDialog(
			modal=True,
			title=ft.Text("Sucesso!", color=ft.Colors.GREEN_600),
			content=ft.Text("Curva cadastrada com sucesso!"),
			actions=[
				ft.ElevatedButton(
					text="OK",
					bgcolor=ft.Colors.GREEN_700,
					color=ft.Colors.WHITE,
					on_click=lambda e: self.page.close(success_dialog),
				)
			],
		)
		self.page.open(success_dialog)


# ============================================
# FUNÇÃO PRINCIPAL - USE ESTA NO SEU CÓDIGO
# ============================================

def create_precos_content(page: ft.Page, screen: Any = None) -> ft.Control:
	"""
	Cria o conteúdo da tela de Preços com dialog de nova curva integrado
	"""

	def on_save_curva(dados: dict, modo: str, trader_id: str = None):
		"""Callback para salvar a curva no banco"""
		print(f"✅ Salvando curva via {modo}")
		print(f"📊 Trader: {trader_id}")
		print(f"📈 Dados: {dados}")

	# TODO: Implementar salvamento no Supabase

	def open_nova_curva_dialog(e):
		dialog = NovaCurvaDialog(page, on_save=on_save_curva)
		dialog.show()

	# Cards de Ação
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
			ink=True,
		)

	cards_row = ft.Row(
		controls=[
			action_card(ft.Icons.ADD_CIRCLE_OUTLINE, "Novo Preço", "Cadastrar curva", on_click=open_nova_curva_dialog),
			action_card(ft.Icons.SEARCH, "Buscar Preço", "Consultar histórico"),
			action_card(ft.Icons.LIST_ALT, "Meus Preços", "Gerenciar cadastros"),
			action_card(ft.Icons.SETTINGS, "Configurações", "Parâmetros gerais"),
		],
		spacing=20,
		alignment=ft.MainAxisAlignment.START,
	)

	# Botões
	buttons_row = ft.Row(
		controls=[
			ft.ElevatedButton(
				text="Adicionar Filtro",
				bgcolor=ft.Colors.BLUE_700,
				color=ft.Colors.WHITE,
			),
			ft.ElevatedButton(
				text="Exportar Dados",
				bgcolor=ft.Colors.BLUE_700,
				color=ft.Colors.WHITE,
			),
		],
		spacing=15,
	)

	# Gráficos
	def chart_placeholder(title: str) -> ft.Control:
		return ft.Container(
			content=ft.Column(
				controls=[
					ft.Text(title, size=14, weight=ft.FontWeight.W_600),
					ft.Container(
						content=ft.Text("Gráfico aqui", color=ft.Colors.GREY_400),
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
			height=250,
			padding=10,
		)

	charts_section = ft.Container(
		content=ft.Column(
			controls=[
				ft.Text("Preços Médios de Energia", size=18, weight=ft.FontWeight.BOLD),
				ft.Row(
					controls=[
						chart_placeholder("Preço PLD - Últimos 12 Meses"),
						chart_placeholder("Preço CCEAL - Último Ano"),
					],
					spacing=20,
					expand=True,
				),
			],
			spacing=20,
		),
		bgcolor=ft.Colors.WHITE,
		border_radius=12,
		padding=25,
		shadow=ft.BoxShadow(spread_radius=1, blur_radius=10, color=ft.Colors.GREY_100),
		height=400,
	)

	# Montagem final
	content = ft.Column(
		controls=[
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
		bgcolor=ft.Colors.GREY_50,
	)


# ============================================
# EXEMPLO DE USO STANDALONE
# ============================================

def main(page: ft.Page):
	page.title = "Gestão de Preços"
	page.add(create_precos_content(page))


if __name__ == "__main__":
	ft.app(target=main)
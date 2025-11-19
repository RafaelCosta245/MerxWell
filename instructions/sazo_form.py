import flet as ft
from datetime import datetime


def main(page: ft.Page):
	page.title = "Sazonalidade de Contrato"
	page.padding = 20
	page.scroll = "auto"
	page.bgcolor = ft.Colors.WHITE
	page.horizontal_alignment = ft.CrossAxisAlignment.CENTER

	# Dados pré-definidos
	contrato = "CONT-2025-001"
	ano_inicio = 2025
	ano_fim = 2027

	# Armazenar dados
	form_data = {}

	# Meses
	meses = ["Jan", "Fev", "Mar", "Abr", "Mai", "Jun", "Jul", "Ago", "Set", "Out", "Nov", "Dez"]
	meses_keys = ["january", "february", "march", "april", "may", "june", "july", "august", "september", "october",
				  "november", "december"]

	# Armazenar referências das linhas
	linhas_refs = []

	def criar_campo(width=80, on_change=None):
		return ft.TextField(
			text_align=ft.TextAlign.CENTER,
			border_color=ft.Colors.GREY_400,
			focused_border_color=ft.Colors.BLACK,
			color=ft.Colors.BLACK,
			width=width,
			height=40,
			text_size=12,
			on_change=on_change,
		)

	def copiar_primeira_linha(e):
		if not linhas_refs or len(linhas_refs) < 2:
			return

		primeira_linha = linhas_refs[0]

		# Copiar para todas as linhas abaixo
		for i in range(1, len(linhas_refs)):
			linha = linhas_refs[i]

			# Copiar preço
			linha['preco'].value = primeira_linha['preco'].value
			# Copiar garantia
			linha['garantia'].value = primeira_linha['garantia'].value
			# Copiar todos os meses
			for j in range(12):
				linha['meses'][j].value = primeira_linha['meses'][j].value

		page.update()
		page.show_snack_bar(
			ft.SnackBar(
				content=ft.Text("✅ Dados copiados para todas as linhas!"),
				bgcolor=ft.Colors.GREEN_600,
			)
		)

	def atualizar_dados(ano, campo, valor):
		if ano not in form_data:
			form_data[ano] = {'year': ano, 'contract_id': contrato}

		if campo in ['price_energy', 'medium_volume'] or campo in meses_keys:
			try:
				form_data[ano][campo] = float(valor) if valor else None
			except ValueError:
				form_data[ano][campo] = None
		else:
			form_data[ano][campo] = valor

	def criar_linha_ano(ano, is_first=False):
		campos_meses = []
		refs = {}

		# Campo preço
		preco_field = criar_campo(
			width=100,
			on_change=lambda e: atualizar_dados(ano, 'price_energy', e.control.value)
		)
		refs['preco'] = preco_field

		# Switch garantia
		garantia_switch = ft.Switch(
			value=False,
			active_color=ft.Colors.BLACK,
			height=30,
			on_change=lambda e: atualizar_dados(ano, 'financial_guarantee', e.control.value)
		)
		refs['garantia'] = garantia_switch

		# Campos dos meses
		for mes_key in meses_keys:
			campo = criar_campo(
				on_change=lambda e, mk=mes_key: atualizar_dados(ano, mk, e.control.value)
			)
			campos_meses.append(campo)
		refs['meses'] = campos_meses

		# Botão de copiar (apenas na primeira linha)
		botao_copiar = None
		if is_first:
			botao_copiar = ft.IconButton(
				icon=ft.Icons.CONTENT_COPY,
				icon_color=ft.Colors.BLUE_700,
				tooltip="Copiar dados para todas as linhas abaixo",
				on_click=copiar_primeira_linha,
			)
		else:
			botao_copiar = ft.Container(width=40)

		linha = ft.Row(
			controls=[
						 botao_copiar,
						 ft.Container(
							 content=ft.Text(str(ano), size=14, weight=ft.FontWeight.BOLD),
							 width=60,
							 alignment=ft.alignment.center,
						 ),
						 preco_field,
						 ft.Container(
							 content=garantia_switch,
							 width=60,
							 alignment=ft.alignment.center,
						 ),
					 ] + campos_meses,
			spacing=5,
			alignment=ft.MainAxisAlignment.START,
		)

		linhas_refs.append(refs)
		return linha

	def salvar_dados(e):
		if not form_data:
			page.show_snack_bar(
				ft.SnackBar(
					content=ft.Text("⚠ Preencha os dados primeiro!"),
					bgcolor=ft.Colors.ORANGE_600,
				)
			)
			return

		# Adicionar timestamps
		for ano in form_data:
			form_data[ano]['created_at'] = datetime.now().isoformat()
			form_data[ano]['updated_at'] = datetime.now().isoformat()

		print("\n" + "=" * 80)
		print("✅ DADOS DAS SAZONALIDADES")
		print("=" * 80)
		for ano in sorted(form_data.keys()):
			print(f"\n📅 ANO {ano}:")
			print("-" * 80)
			for key, value in form_data[ano].items():
				print(f"  {key}: {value}")
		print("\n" + "=" * 80)

		page.show_snack_bar(
			ft.SnackBar(
				content=ft.Text(f"✅ {len(form_data)} sazonalidade(s) salva(s)!"),
				bgcolor=ft.Colors.GREEN_600,
			)
		)

	# Cabeçalho da planilha
	cabecalho = ft.Row(
		controls=[
					 ft.Container(width=40),  # Espaço do botão
					 ft.Container(
						 content=ft.Text("Ano", size=12, weight=ft.FontWeight.BOLD),
						 width=60,
						 alignment=ft.alignment.center,
					 ),
					 ft.Container(
						 content=ft.Text("Preço R$/MWh", size=12, weight=ft.FontWeight.BOLD),
						 width=100,
						 alignment=ft.alignment.center,
					 ),
					 ft.Container(
						 content=ft.Text("Garantia", size=12, weight=ft.FontWeight.BOLD),
						 width=60,
						 alignment=ft.alignment.center,
					 ),
				 ] + [
					 ft.Container(
						 content=ft.Text(mes, size=12, weight=ft.FontWeight.BOLD),
						 width=80,
						 alignment=ft.alignment.center,
					 ) for mes in meses
				 ],
		spacing=5,
	)

	# Criar linhas para cada ano
	linhas = []
	for idx, ano in enumerate(range(ano_inicio, ano_fim + 1)):
		form_data[ano] = {'year': ano, 'contract_id': contrato}
		linhas.append(criar_linha_ano(ano, is_first=(idx == 0)))

	# Layout
	page.add(
		ft.Column([
			# Título
			ft.Container(
				content=ft.Text(
					f"Sazonalidade: {contrato} ({ano_inicio}-{ano_fim})",
					size=20,
					weight=ft.FontWeight.BOLD,
				),
				padding=10,
			),

			# Planilha
			ft.Container(
				content=ft.Column([
					cabecalho,
					ft.Divider(height=1, color=ft.Colors.BLACK),
					*linhas,
				], spacing=2),
				padding=10,
				border=ft.border.all(1, ft.Colors.BLACK),
				bgcolor=ft.Colors.GREY_50,
			),

			# Botões
			ft.Row([
				ft.ElevatedButton(
					"Cancelar",
					icon=ft.Icons.CANCEL,
					style=ft.ButtonStyle(
						color=ft.Colors.WHITE,
						bgcolor=ft.Colors.RED_700,
					),
				),
				ft.ElevatedButton(
					"Salvar",
					icon=ft.Icons.CHECK,
					on_click=salvar_dados,
					style=ft.ButtonStyle(
						color=ft.Colors.WHITE,
						bgcolor=ft.Colors.GREEN_700,
					),
				),
			], spacing=10),

		], spacing=20, horizontal_alignment=ft.CrossAxisAlignment.CENTER)
	)


ft.app(target=main)
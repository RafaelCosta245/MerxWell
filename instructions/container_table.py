import flet as ft


def main(page: ft.Page):
	page.title = "Tabela Customizada"
	page.padding = 30
	page.scroll = "auto"
	page.bgcolor = ft.Colors.GREY_100
	page.horizontal_alignment = ft.CrossAxisAlignment.CENTER

	# Dados da tabela (exemplo)
	headers = ["ID", "Nome", "Categoria", "Valor (R$)", "Status", "Editar", "Adicionar", "Excluir"]

	data = [
		["001", "Produto A", "Eletrônicos", "1.250,00", "Ativo"],
		["002", "Produto B", "Alimentos", "45,90", "Ativo"],
		["003", "Produto C", "Vestuário", "89,99", "Inativo"],
		["004", "Produto D", "Eletrônicos", "2.499,00", "Ativo"],
		["005", "Produto E", "Casa", "350,00", "Ativo"],
		["006", "Produto F", "Esportes", "199,90", "Inativo"],
		["007", "Produto G", "Livros", "59,90", "Ativo"],
		["008", "Produto H", "Eletrônicos", "899,00", "Ativo"],
		["009", "Produto I", "Alimentos", "23,50", "Ativo"],
		["010", "Produto J", "Vestuário", "149,90", "Inativo"],
	]

	# Função para criar célula do cabeçalho
	def criar_celula_header(texto, largura):
		return ft.Container(
			content=ft.Text(
				texto,
				size=14,
				weight=ft.FontWeight.BOLD,
				color=ft.Colors.WHITE,
				text_align=ft.TextAlign.CENTER,
			),
			width=largura,
			height=50,
			bgcolor=ft.Colors.BLUE_700,
			padding=10,
			alignment=ft.alignment.center,
			border=ft.border.all(1, ft.Colors.BLUE_900),
		)

	# Função para criar célula de dados
	def criar_celula_dados(texto, largura, index):
		# Alterna cor de fundo para melhor legibilidade
		bg_color = ft.Colors.WHITE if index % 2 == 0 else ft.Colors.GREY_50

		# Cor especial para status
		text_color = ft.Colors.BLACK
		if texto == "Ativo":
			text_color = ft.Colors.GREEN_700
		elif texto == "Inativo":
			text_color = ft.Colors.RED_700

		return ft.Container(
			content=ft.Text(
				texto,
				size=13,
				color=text_color,
				weight=ft.FontWeight.W_500 if texto in ["Ativo", "Inativo"] else ft.FontWeight.NORMAL,
				text_align=ft.TextAlign.CENTER,
			),
			width=largura,
			height=45,
			bgcolor=bg_color,
			padding=10,
			alignment=ft.alignment.center,
			border=ft.border.all(1, ft.Colors.GREY_300),
		)

	# Função para criar botão de ação
	def criar_botao_acao(tipo, dados_linha, index):
		bg_color = ft.Colors.WHITE if index % 2 == 0 else ft.Colors.GREY_50

		# Configurações por tipo de botão
		config = {
			"editar": {
				"icon": ft.Icons.EDIT,
				"color": ft.Colors.BLUE_600,
				"tooltip": "Editar",
			},
			"adicionar": {
				"icon": ft.Icons.ADD_CIRCLE,
				"color": ft.Colors.GREEN_600,
				"tooltip": "Adicionar",
			},
			"excluir": {
				"icon": ft.Icons.DELETE,
				"color": ft.Colors.RED_600,
				"tooltip": "Excluir",
			},
		}

		def on_click(e):
			print(f"\n=== Ação: {tipo.upper()} ===")
			print(f"ID: {dados_linha[0]}")
			print(f"Nome: {dados_linha[1]}")
			print(f"Categoria: {dados_linha[2]}")
			print(f"Valor: {dados_linha[3]}")
			print(f"Status: {dados_linha[4]}")
			print("=" * 30)

		return ft.Container(
			content=ft.IconButton(
				icon=config[tipo]["icon"],
				icon_color=config[tipo]["color"],
				tooltip=config[tipo]["tooltip"],
				on_click=on_click,
			),
			width=90,
			height=45,
			bgcolor=bg_color,
			alignment=ft.alignment.center,
			border=ft.border.all(1, ft.Colors.GREY_300),
		)

	# Larguras das colunas
	larguras = [80, 200, 150, 150, 120, 90, 90, 90]

	# Criar cabeçalho
	header_row = ft.Row(
		controls=[
			criar_celula_header(headers[i], larguras[i])
			for i in range(len(headers))
		],
		spacing=0,
	)

	# Criar linhas de dados
	data_rows = []
	for idx, row in enumerate(data):
		data_row = ft.Row(
			controls=[
				# Células de dados
				criar_celula_dados(row[0], larguras[0], idx),
				criar_celula_dados(row[1], larguras[1], idx),
				criar_celula_dados(row[2], larguras[2], idx),
				criar_celula_dados(row[3], larguras[3], idx),
				criar_celula_dados(row[4], larguras[4], idx),
				# Botões de ação
				criar_botao_acao("editar", row, idx),
				criar_botao_acao("adicionar", row, idx),
				criar_botao_acao("excluir", row, idx),
			],
			spacing=0,
		)
		data_rows.append(data_row)

	# Calcular largura total da tabela
	largura_total = sum(larguras)

	# Container da tabela
	tabela = ft.Container(
		content=ft.Column(
			controls=[header_row] + data_rows,
			spacing=0,
			scroll=ft.ScrollMode.AUTO,
		),
		width=largura_total,
		border=ft.border.all(2, ft.Colors.BLUE_700),
		border_radius=8,
		padding=0,
	)

	# Layout da página
	page.add(
		ft.Column(
			controls=[
				# Título
				ft.Text(
					"📋 Tabela de Produtos",
					size=28,
					weight=ft.FontWeight.BOLD,
					color=ft.Colors.BLUE_900,
					text_align=ft.TextAlign.CENTER,
				),

				# Subtítulo
				ft.Text(
					"Listagem completa com 10 registros",
					size=14,
					color=ft.Colors.GREY_700,
					italic=True,
					text_align=ft.TextAlign.CENTER,
				),

				ft.Divider(height=20, color=ft.Colors.TRANSPARENT),

				# Tabela
				tabela,

				ft.Divider(height=20, color=ft.Colors.TRANSPARENT),

				# Informações adicionais
				ft.Container(
					content=ft.Row([
						ft.Icon(ft.Icons.INFO_OUTLINE, color=ft.Colors.BLUE_700, size=20),
						ft.Text(
							"Clique nos botões para ver os dados da linha no console",
							size=12,
							color=ft.Colors.GREY_700,
						),
					], spacing=10),
					width=largura_total,
					padding=10,
					bgcolor=ft.Colors.BLUE_50,
					border_radius=8,
				),

				# Legenda de ações
				ft.Container(
					content=ft.Column([
						ft.Text("Ações Disponíveis:", size=14, weight=ft.FontWeight.BOLD),
						ft.Row([
							ft.Row([
								ft.Icon(ft.Icons.EDIT, color=ft.Colors.BLUE_600, size=16),
								ft.Text("Editar registro", size=12),
							], spacing=6),
							ft.Row([
								ft.Icon(ft.Icons.ADD_CIRCLE, color=ft.Colors.GREEN_600, size=16),
								ft.Text("Adicionar item", size=12),
							], spacing=6),
							ft.Row([
								ft.Icon(ft.Icons.DELETE, color=ft.Colors.RED_600, size=16),
								ft.Text("Excluir registro", size=12),
							], spacing=6),
						], spacing=20, wrap=True),
					], spacing=8),
					width=largura_total,
					padding=15,
					bgcolor=ft.Colors.WHITE,
					border_radius=8,
					border=ft.border.all(1, ft.Colors.GREY_300),
				),

			],
			spacing=15,
			horizontal_alignment=ft.CrossAxisAlignment.CENTER,
		)
	)


ft.app(target=main)
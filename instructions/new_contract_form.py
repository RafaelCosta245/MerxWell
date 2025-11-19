import flet as ft
from datetime import datetime


def main(page: ft.Page):
	page.title = "Cadastro de Contratos"
	page.padding = 30
	page.scroll = "auto"
	page.bgcolor = ft.Colors.WHITE
	page.horizontal_alignment = ft.CrossAxisAlignment.CENTER

	# Dicionário para armazenar os valores dos campos
	form_data = {}

	# Função para criar campo de texto
	def criar_campo(label, hint="", obrigatorio=False, width=None, multiline=False, key=None):
		field = ft.TextField(
			hint_text=hint,
			border_color=ft.Colors.BLACK,
			focused_border_color=ft.Colors.BLACK,
			color=ft.Colors.BLACK,
			filled=True,
			bgcolor=ft.Colors.WHITE,
			multiline=multiline,
			min_lines=3 if multiline else 1,
			max_lines=5 if multiline else 1,
			on_change=lambda e: form_data.update({key: e.control.value}) if key else None,
		)

		return ft.Container(
			content=ft.Column([
				ft.Row([
					ft.Text(label, size=13, weight=ft.FontWeight.W_500, color=ft.Colors.BLACK),
					ft.Text("*", color=ft.Colors.RED_700, size=13) if obrigatorio else ft.Container(),
				], spacing=3),
				field,
			], spacing=5),
			width=width,
		)

	# Função para criar dropdown
	def criar_dropdown(label, opcoes, obrigatorio=False, width=None, key=None, on_change_custom=None):
		def handle_change(e):
			if key:
				form_data[key] = e.control.value
			if on_change_custom:
				on_change_custom(e)

		dropdown = ft.Dropdown(
			options=[ft.dropdown.Option(op) for op in opcoes],
			border_color=ft.Colors.BLACK,
			focused_border_color=ft.Colors.BLACK,
			color=ft.Colors.BLACK,
			filled=True,
			bgcolor=ft.Colors.WHITE,
			on_change=handle_change,
		)

		return ft.Container(
			content=ft.Column([
				ft.Row([
					ft.Text(label, size=13, weight=ft.FontWeight.W_500, color=ft.Colors.BLACK),
					ft.Text("*", color=ft.Colors.RED_700, size=13) if obrigatorio else ft.Container(),
				], spacing=3),
				dropdown,
			], spacing=5),
			width=width,
		), dropdown

	# Função para criar campo de data
	def criar_data(label, obrigatorio=False, width=None, key=None):
		field = ft.TextField(
			hint_text="dd/mm/aaaa",
			border_color=ft.Colors.BLACK,
			focused_border_color=ft.Colors.BLACK,
			color=ft.Colors.BLACK,
			filled=True,
			bgcolor=ft.Colors.WHITE,
			on_change=lambda e: form_data.update({key: e.control.value}) if key else None,
		)

		def pick_date(e):
			date_picker.pick_date()

		def date_changed(e):
			if e.control.value:
				field.value = e.control.value.strftime("%d/%m/%Y")
				if key:
					form_data[key] = e.control.value.isoformat()
				page.update()

		date_picker = ft.DatePicker(on_change=date_changed)
		page.overlay.append(date_picker)

		field.suffix = ft.IconButton(
			icon=ft.Icons.CALENDAR_MONTH,
			on_click=pick_date,
			icon_color=ft.Colors.BLACK,
		)

		return ft.Container(
			content=ft.Column([
				ft.Row([
					ft.Text(label, size=13, weight=ft.FontWeight.W_500, color=ft.Colors.BLACK),
					ft.Text("*", color=ft.Colors.RED_700, size=13) if obrigatorio else ft.Container(),
				], spacing=3),
				field,
			], spacing=5),
			width=width,
		)

	# Função para criar switch
	def criar_switch(label, descricao="", key=None):
		switch = ft.Switch(
			value=False,
			active_color=ft.Colors.BLACK,
			on_change=lambda e: form_data.update({key: e.control.value}) if key else None,
		)

		return ft.Container(
			content=ft.Row([
				ft.Column([
					ft.Text(label, size=14, weight=ft.FontWeight.W_500, color=ft.Colors.BLACK),
					ft.Text(descricao, size=12, color=ft.Colors.GREY_700) if descricao else ft.Container(),
				], spacing=2, expand=True),
				switch,
			], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
			padding=10,
			bgcolor=ft.Colors.WHITE,
			border_radius=8,
			border=ft.border.all(1, ft.Colors.BLACK),
		)

	# Função para criar checkbox
	def criar_checkbox(label, key=None):
		return ft.Checkbox(
			label=label,
			value=False,
			fill_color=ft.Colors.BLACK,
			check_color=ft.Colors.WHITE,
			on_change=lambda e: form_data.update({key: e.control.value}) if key else None,
		)

	# Campo de prestador (será preenchido automaticamente)
	prestador_field = ft.TextField(
		hint_text="Selecionado automaticamente da comercializadora",
		border_color=ft.Colors.BLACK,
		focused_border_color=ft.Colors.BLACK,
		color=ft.Colors.BLACK,
		filled=True,
		bgcolor=ft.Colors.GREY_200,
		read_only=True,
	)

	# Função para sincronizar comercializadora com prestador
	def sync_comercializadora(e):
		prestador_field.value = e.control.value
		form_data['service_provider'] = e.control.value
		page.update()

	# Dropdown de comercializadora
	comercializadora_container, comercializadora_dropdown = criar_dropdown(
		"Comercializadora Vinculada",
		["Comercializadora A", "Comercializadora B", "Comercializadora C", "Nenhuma"],
		obrigatorio=True,
		width=820,
		key='trader_id',
		on_change_custom=sync_comercializadora
	)

	# ==================== ABA 1: DADOS GERAIS ====================
	aba1_content = ft.Container(
		content=ft.Column([
			ft.Text("Informações Básicas do Contrato", size=18, weight=ft.FontWeight.BOLD, color=ft.Colors.BLACK),
			ft.Divider(height=20, color=ft.Colors.BLACK),

			# Comercializadora
			comercializadora_container,

			# Linha 1: Prestador e Contratante
			ft.Row([
				ft.Container(
					content=ft.Column([
						ft.Row([
							ft.Text("Prestador de Serviço", size=13, weight=ft.FontWeight.W_500, color=ft.Colors.BLACK),
							ft.Text("*", color=ft.Colors.RED_700, size=13),
						], spacing=3),
						prestador_field,
					], spacing=5),
					width=400,
				),
				criar_campo("Contratante", "Nome da empresa cliente", obrigatorio=True, width=400, key='contractor'),
			], spacing=20),

			# Linha 2: Tipo e Código
			ft.Row([
				criar_dropdown(
					"Tipo de Contrato",
					["ATACADISTA", "VAREJISTA", "DISTRIBUIDOR", "GERADOR"],
					obrigatorio=True,
					width=400,
					key='contract_type'
				)[0],
				criar_campo("Código do Contrato", "Ex: CONT-2025-001", obrigatorio=True, width=400,
							key='contract_code'),
			], spacing=20),

			# Linha 3: Datas
			ft.Row([
				criar_data("Data de Início", obrigatorio=True, width=400, key='contract_start_date'),
				criar_data("Data de Término", obrigatorio=True, width=400, key='contract_end_date'),
			], spacing=20),

			# Nota
			ft.Container(
				content=ft.Row([
					ft.Icon(ft.Icons.INFO_OUTLINE, color=ft.Colors.BLACK, size=20),
					ft.Text(
						"As datas definem o período de vigência do contrato de energia.",
						size=12,
						color=ft.Colors.BLACK,
					),
				], spacing=10),
				padding=10,
				bgcolor=ft.Colors.WHITE,
				border_radius=8,
				border=ft.border.all(1, ft.Colors.BLACK),
			),

		], spacing=20, scroll=ft.ScrollMode.AUTO),
		padding=20,
	)

	# ==================== ABA 2: COMERCIAL ====================
	aba2_content = ft.Container(
		content=ft.Column([
			ft.Text("Dados Comerciais", size=18, weight=ft.FontWeight.BOLD, color=ft.Colors.BLACK),
			ft.Divider(height=20, color=ft.Colors.BLACK),

			# Taxa de Fee
			ft.Row([
				criar_campo("Taxa de Fee (R$/MWh)", "Ex: 2.5", width=400, key='fee_tax'),
				criar_campo("Data da Nota de Energia (du)", "Dia de vencimento", width=400, key='energy_note_date'),
			], spacing=20),

			# Checkboxes
			ft.Text("Descontos e Benefícios", size=15, weight=ft.FontWeight.W_500, color=ft.Colors.BLACK),
			ft.Container(
				content=ft.Column([
					criar_checkbox("Possui Desconto PROINFA", key='has_proinfa_discount'),
					criar_checkbox("Garantia Financeira Ativa", key='financial_guarantee'),
				], spacing=10),
				padding=15,
				bgcolor=ft.Colors.WHITE,
				border_radius=8,
				border=ft.border.all(1, ft.Colors.BLACK),
			),

			# Nota
			ft.Container(
				content=ft.Row([
					ft.Icon(ft.Icons.ATTACH_MONEY, color=ft.Colors.BLACK, size=20),
					ft.Text(
						"PROINFA: Programa de Incentivo às Fontes Alternativas de Energia Elétrica.",
						size=12,
						color=ft.Colors.BLACK,
					),
				], spacing=10),
				padding=10,
				bgcolor=ft.Colors.WHITE,
				border_radius=8,
				border=ft.border.all(1, ft.Colors.BLACK),
			),

		], spacing=20, scroll=ft.ScrollMode.AUTO),
		padding=20,
	)

	# ==================== ABA 3: TÉCNICO ====================
	aba3_content = ft.Container(
		content=ft.Column([
			ft.Text("Parâmetros Técnicos", size=18, weight=ft.FontWeight.BOLD, color=ft.Colors.BLACK),
			ft.Divider(height=20, color=ft.Colors.BLACK),

			# Linha 1: Fonte e Submercado
			ft.Row([
				criar_dropdown(
					"Tipo de Fonte de Energia",
					["CONVENCIONAL", "I5", "I1", "CQ5"],
					obrigatorio=True,
					width=400,
					key='energy_source_type'
				)[0],
				criar_dropdown(
					"Submercado",
					["NORTE", "NORDESTE", "SUL", "SUDESTE"],
					obrigatorio=True,
					width=400,
					key='submarket'
				)[0],
			], spacing=20),

			# Fator de Carga
			ft.Text("Fator de Carga", size=15, weight=ft.FontWeight.W_500, color=ft.Colors.BLACK),
			ft.Row([
				criar_campo("Fator de Carga (%)", "Ex: 85.5", width=820, key='power_load_factor'),
			], spacing=20),

			ft.Divider(height=10, color=ft.Colors.TRANSPARENT),

			# Flexibilidade
			ft.Text("Flexibilidade", size=15, weight=ft.FontWeight.W_500, color=ft.Colors.BLACK),
			ft.Row([
				criar_campo("Flex Mínima (%)", "Ex: -10", width=400, key='flex_min'),
				criar_campo("Flex Máxima (%)", "Ex: +10", width=400, key='flex_max'),
			], spacing=20),

			# Sazonalidade
			ft.Text("Sazonalidade", size=15, weight=ft.FontWeight.W_500, color=ft.Colors.BLACK),
			ft.Row([
				criar_campo("Sazonalidade Mínima (%)", "Ex: -20", width=400, key='seasonality_min'),
				criar_campo("Sazonalidade Máxima (%)", "Ex: +20", width=400, key='seasonality_max'),
			], spacing=20),

			# Perdas
			ft.Text("Perdas Técnicas", size=15, weight=ft.FontWeight.W_500, color=ft.Colors.BLACK),
			ft.Row([
				criar_campo("Percentual de Perdas (%)", "Ex: 3.0", width=820, key='looses'),
			], spacing=20),

		], spacing=20, scroll=ft.ScrollMode.AUTO),
		padding=20,
	)

	# ==================== ABA 4: CONFIGURAÇÕES ====================
	aba4_content = ft.Container(
		content=ft.Column([
			ft.Text("Configurações do Sistema", size=18, weight=ft.FontWeight.BOLD, color=ft.Colors.BLACK),
			ft.Divider(height=20, color=ft.Colors.BLACK),

			# Switches
			ft.Text("Status e Automações", size=15, weight=ft.FontWeight.W_500, color=ft.Colors.BLACK),
			criar_switch(
				"Contrato Ativo",
				"Define se o contrato está em vigor e pode ser utilizado no sistema",
				key='is_active'
			),
			ft.Divider(height=10, color=ft.Colors.TRANSPARENT),
			criar_switch(
				"Faturamento Automático Liberado",
				"Permite que o sistema gere faturas automaticamente para este contrato",
				key='automatic_billing_released'
			),

			ft.Divider(height=20, color=ft.Colors.BLACK),

			# Informações de auditoria
			ft.Container(
				content=ft.Column([
					ft.Text("Informações de Auditoria", size=14, weight=ft.FontWeight.W_500, color=ft.Colors.BLACK),
					ft.Divider(height=5, color=ft.Colors.TRANSPARENT),
					ft.Row([
						ft.Icon(ft.Icons.CALENDAR_TODAY, size=16, color=ft.Colors.BLACK),
						ft.Text(f"Criado em: {datetime.now().strftime('%d/%m/%Y às %H:%M')}", size=12,
								color=ft.Colors.BLACK),
					], spacing=5),
					ft.Row([
						ft.Icon(ft.Icons.UPDATE, size=16, color=ft.Colors.BLACK),
						ft.Text(f"Última atualização: {datetime.now().strftime('%d/%m/%Y às %H:%M')}", size=12,
								color=ft.Colors.BLACK),
					], spacing=5),
				], spacing=8),
				padding=15,
				bgcolor=ft.Colors.WHITE,
				border_radius=8,
				border=ft.border.all(1, ft.Colors.BLACK),
			),

		], spacing=20, scroll=ft.ScrollMode.AUTO),
		padding=20,
	)

	# ==================== SISTEMA DE ABAS ====================
	tabs = ft.Tabs(
		selected_index=0,
		animation_duration=300,
		label_color=ft.Colors.BLACK,
		indicator_color=ft.Colors.BLACK,
		tabs=[
			ft.Tab(
				text="Dados Gerais",
				icon=ft.Icons.DESCRIPTION,
				content=aba1_content,
			),
			ft.Tab(
				text="Comercial",
				icon=ft.Icons.ATTACH_MONEY,
				content=aba2_content,
			),
			ft.Tab(
				text="Técnico",
				icon=ft.Icons.SETTINGS_INPUT_COMPONENT,
				content=aba3_content,
			),
			ft.Tab(
				text="Configurações",
				icon=ft.Icons.SETTINGS,
				content=aba4_content,
			),
		],
		expand=1,
	)

	# ==================== BOTÕES DE AÇÃO ====================
	def salvar_contrato(e):
		# Adicionar timestamps
		form_data['created_at'] = datetime.now().isoformat()
		form_data['updated_at'] = datetime.now().isoformat()

		print("\n" + "=" * 60)
		print("✅ DADOS DO CONTRATO PARA SALVAR")
		print("=" * 60)
		print("\nDicionário completo:")
		print(form_data)
		print("\n" + "=" * 60)

		page.show_snack_bar(
			ft.SnackBar(
				content=ft.Text("✅ Contrato salvo com sucesso!"),
				bgcolor=ft.Colors.GREEN_600,
			)
		)

	def cancelar(e):
		print("\n❌ Cancelado pelo usuário")
		page.show_snack_bar(
			ft.SnackBar(
				content=ft.Text("❌ Operação cancelada"),
				bgcolor=ft.Colors.RED_600,
			)
		)

	botoes = ft.Container(
		content=ft.Row([
			ft.ElevatedButton(
				"Cancelar",
				icon=ft.Icons.CANCEL,
				on_click=cancelar,
				style=ft.ButtonStyle(
					color=ft.Colors.WHITE,
					bgcolor=ft.Colors.RED_700,
				),
				width=200,
				height=50,
			),
			ft.ElevatedButton(
				"Salvar Contrato",
				icon=ft.Icons.CHECK_CIRCLE,
				on_click=salvar_contrato,
				style=ft.ButtonStyle(
					color=ft.Colors.WHITE,
					bgcolor=ft.Colors.BLACK,
				),
				width=200,
				height=50,
			),
		], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
		padding=20,
	)

	# ==================== LAYOUT PRINCIPAL ====================
	page.add(
		ft.Column([
			# Cabeçalho
			ft.Container(
				content=ft.Column([
					ft.Row([
						ft.Icon(ft.Icons.ENERGY_SAVINGS_LEAF, size=40, color=ft.Colors.BLACK),
						ft.Column([
							ft.Text("Cadastro de Contrato de Energia", size=26, weight=ft.FontWeight.BOLD,
									color=ft.Colors.BLACK),
							ft.Text("Preencha todos os campos obrigatórios (*)", size=13, color=ft.Colors.BLACK),
						], spacing=2),
					], spacing=15),
				], spacing=10),
				padding=20,
				bgcolor=ft.Colors.WHITE,
				border_radius=10,
				border=ft.border.all(2, ft.Colors.BLACK),
				width=900,
			),

			# Container das abas
			ft.Container(
				content=tabs,
				bgcolor=ft.Colors.WHITE,
				border_radius=10,
				border=ft.border.all(2, ft.Colors.BLACK),
				width=900,
				height=600,
			),

			# Botões
			ft.Container(
				content=botoes,
				bgcolor=ft.Colors.WHITE,
				border_radius=10,
				border=ft.border.all(2, ft.Colors.BLACK),
				width=900,
			),

		], spacing=20, horizontal_alignment=ft.CrossAxisAlignment.CENTER)
	)


ft.app(target=main)
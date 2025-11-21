import flet as ft
from datetime import datetime


def validar_data(data):
	"""
	Valida se a data é válida no formato dd/mm/aaaa
	Retorna True se válida, False caso contrário
	"""
	# Remove caracteres não numéricos
	data_limpa = ''.join(filter(str.isdigit, data))

	# Verifica se tem 8 dígitos
	if len(data_limpa) != 8:
		return False

	try:
		dia = int(data_limpa[:2])
		mes = int(data_limpa[2:4])
		ano = int(data_limpa[4:8])

		# Verifica se dia, mês e ano são válidos
		if dia < 1 or dia > 31:
			return False
		if mes < 1 or mes > 12:
			return False
		if ano < 1900 or ano > 2100:
			return False

		# Tenta criar a data para validar (ex: 31/02 será inválido)
		datetime(ano, mes, dia)
		return True
	except ValueError:
		return False


def aplicar_mascara_data(e):
	"""
	Aplica máscara de data no formato: dd/mm/aaaa
	"""
	# Remove tudo que não é número
	valor = ''.join(filter(str.isdigit, e.control.value))

	# Limita a 8 dígitos (ddmmaaaa)
	valor = valor[:8]

	# Aplica a máscara
	valor_formatado = ''

	if len(valor) > 0:
		valor_formatado = valor[:2]  # dd
	if len(valor) > 2:
		valor_formatado += '/' + valor[2:4]  # mm
	if len(valor) > 4:
		valor_formatado += '/' + valor[4:8]  # aaaa

	# Atualiza o TextField
	e.control.value = valor_formatado

	# Valida a data se tiver 8 dígitos
	if len(valor) == 8:
		if validar_data(valor):
			e.control.error_text = None
			e.control.border_color = ft.Colors.GREEN
		else:
			e.control.error_text = "Data inválida"
			e.control.border_color = ft.Colors.RED
	else:
		e.control.error_text = None
		e.control.border_color = None

	e.control.update()


def main(page: ft.Page):
	page.title = "Máscara de Data com Validação"
	page.padding = 50

	data_field = ft.TextField(
		label="Data",
		hint_text="dd/mm/aaaa",
		on_change=aplicar_mascara_data,
		width=300
	)

	status_text = ft.Text("", size=16)

	def verificar_data(e):
		# Remove a máscara para obter apenas os números
		valor_limpo = ''.join(filter(str.isdigit, data_field.value))

		if len(valor_limpo) == 0:
			status_text.value = "Digite uma data"
			status_text.color = ft.Colors.GREY
		elif len(valor_limpo) < 8:
			status_text.value = "Data incompleta"
			status_text.color = ft.Colors.ORANGE
		elif validar_data(valor_limpo):
			# Formata a data por extenso
			dia = valor_limpo[:2]
			mes = valor_limpo[2:4]
			ano = valor_limpo[4:8]

			meses = {
				'01': 'janeiro', '02': 'fevereiro', '03': 'março',
				'04': 'abril', '05': 'maio', '06': 'junho',
				'07': 'julho', '08': 'agosto', '09': 'setembro',
				'10': 'outubro', '11': 'novembro', '12': 'dezembro'
			}

			status_text.value = f"✓ Data válida: {dia} de {meses[mes]} de {ano}"
			status_text.color = ft.Colors.GREEN
		else:
			status_text.value = "✗ Data inválida"
			status_text.color = ft.Colors.RED

		page.update()

	botao = ft.ElevatedButton(
		text="Verificar Data",
		on_click=verificar_data
	)

	page.add(
		ft.Column([
			ft.Text("Digite a data:", size=20, weight=ft.FontWeight.BOLD),
			data_field,
			botao,
			status_text,
			ft.Divider(height=20),
			ft.Text("A máscara aceita apenas números e formata automaticamente",
					size=12, color=ft.Colors.GREY_700),
			ft.Text("Exemplo: Digite 25122024 → 25/12/2024",
					size=12, color=ft.Colors.GREY_700),
		])
	)


ft.app(target=main)
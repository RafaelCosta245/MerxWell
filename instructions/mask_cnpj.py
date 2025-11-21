import flet as ft


def validar_cnpj(cnpj):
	"""
    Valida um CNPJ usando o algoritmo de dígitos verificadores
    Retorna True se válido, False caso contrário
    """
	# Remove caracteres não numéricos
	cnpj = ''.join(filter(str.isdigit, cnpj))

	# Verifica se tem 14 dígitos
	if len(cnpj) != 14:
		return False

	# Verifica se todos os dígitos são iguais (CNPJ inválido)
	if cnpj == cnpj[0] * 14:
		return False

	# Calcula o primeiro dígito verificador
	peso = [5, 4, 3, 2, 9, 8, 7, 6, 5, 4, 3, 2]
	soma = sum(int(cnpj[i]) * peso[i] for i in range(12))
	resto = soma % 11
	digito1 = 0 if resto < 2 else 11 - resto

	# Verifica o primeiro dígito
	if int(cnpj[12]) != digito1:
		return False

	# Calcula o segundo dígito verificador
	peso = [6, 5, 4, 3, 2, 9, 8, 7, 6, 5, 4, 3, 2]
	soma = sum(int(cnpj[i]) * peso[i] for i in range(13))
	resto = soma % 11
	digito2 = 0 if resto < 2 else 11 - resto

	# Verifica o segundo dígito
	return int(cnpj[13]) == digito2


def aplicar_mascara_cnpj(e):
	"""
    Aplica máscara de CNPJ no formato: XX.XXX.XXX/XXXX-XX
    """
	# Remove tudo que não é número
	valor = ''.join(filter(str.isdigit, e.control.value))

	# Limita a 14 dígitos
	valor = valor[:14]

	# Aplica a máscara
	valor_formatado = ''

	if len(valor) > 0:
		valor_formatado = valor[:2]
	if len(valor) > 2:
		valor_formatado += '.' + valor[2:5]
	if len(valor) > 5:
		valor_formatado += '.' + valor[5:8]
	if len(valor) > 8:
		valor_formatado += '/' + valor[8:12]
	if len(valor) > 12:
		valor_formatado += '-' + valor[12:14]

	# Atualiza o TextField
	e.control.value = valor_formatado

	# Valida o CNPJ se tiver 14 dígitos
	if len(valor) == 14:
		if validar_cnpj(valor):
			e.control.error_text = None
			e.control.border_color = ft.Colors.GREEN
		else:
			e.control.error_text = "CNPJ inválido"
			e.control.border_color = ft.Colors.RED
	else:
		e.control.error_text = None
		e.control.border_color = None

	e.control.update()


def main(page: ft.Page):
	page.title = "Máscara CNPJ com Validação"
	page.padding = 50

	cnpj_field = ft.TextField(
		label="CNPJ",
		hint_text="00.000.000/0000-00",
		on_change=aplicar_mascara_cnpj,
		width=300
	)

	status_text = ft.Text("", size=16)

	def verificar_cnpj(e):
		# Remove a máscara para obter apenas os números
		valor_limpo = ''.join(filter(str.isdigit, cnpj_field.value))

		if len(valor_limpo) == 0:
			status_text.value = "Digite um CNPJ"
			status_text.color = ft.Colors.GREY
		elif len(valor_limpo) < 14:
			status_text.value = "CNPJ incompleto"
			status_text.color = ft.Colors.ORANGE
		elif validar_cnpj(valor_limpo):
			status_text.value = f"✓ CNPJ válido: {valor_limpo}"
			status_text.color = ft.Colors.GREEN
		else:
			status_text.value = "✗ CNPJ inválido"
			status_text.color = ft.Colors.RED

		page.update()

	botao = ft.ElevatedButton(
		text="Verificar CNPJ",
		on_click=verificar_cnpj
	)

	page.add(
		ft.Column([
			ft.Text("Digite o CNPJ:", size=20, weight=ft.FontWeight.BOLD),
			cnpj_field,
			botao,
			status_text,
			ft.Divider(height=20),
			ft.Text("Exemplos de CNPJs válidos para teste:", size=14, weight=ft.FontWeight.BOLD),
			ft.Text("• 11.222.333/0001-81", size=12, color=ft.Colors.GREY_700),
			ft.Text("• 00.000.000/0001-91", size=12, color=ft.Colors.GREY_700),
		])
	)


ft.app(target=main)
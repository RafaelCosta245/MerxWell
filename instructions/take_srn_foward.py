import pandas as pd
import tkinter as tk
from tkinter import filedialog

# Abre janela para escolher arquivo
root = tk.Tk()
root.withdraw()  # Oculta a janela principal

caminho_arquivo = filedialog.askopenfilename(
    title="Selecione a planilha de preços",
    filetypes=[("Excel Files", "*.xlsx *.xls")]
)

if not caminho_arquivo:
    raise Exception("Nenhum arquivo selecionado!")

# Carrega a planilha
df = pd.read_excel(caminho_arquivo)

# Dicionário final
precos = {}

# Percorre as colunas exceto PRODUTO
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

print("Arquivo carregado com sucesso!")
print(precos)


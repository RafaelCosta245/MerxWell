# Instruções de Path Resolution para cx_Freeze

## Contexto

Este documento descreve como gerenciar caminhos de arquivos no projeto MerxWell para garantir que funcionem tanto em ambiente de desenvolvimento quanto quando o aplicativo é compilado com cx_Freeze.

## Problema

Quando você usa caminhos relativos ou baseados em `__file__` diretamente no código, eles quebram quando o aplicativo é compilado como executável, porque:

1. `__file__` aponta para locais diferentes em desenvolvimento vs. executável congelado
2. `os.getcwd()` pode variar dependendo de onde o executável é chamado
3. Caminhos hardcoded como `"assets/file.txt"` não funcionam se o executável está em outro diretório

## Solução Implementada

### Módulo Helper: `helpers/paths.py`

Foi criado um módulo centralizado que detecta automaticamente o modo de execução e retorna os caminhos corretos.

**Funções disponíveis:**

```python
from helpers.paths import get_base_path, get_asset_path, get_icon_path

# Retorna o diretório base do aplicativo
base = get_base_path()  # Path object

# Retorna caminho completo para um asset
doc_path = get_asset_path("documents", "template.docx")  # Path object

# Retorna caminho para ícone (como string)
icon = get_icon_path("logo.ico")  # str
```

### Como Funciona

O módulo verifica se o app está "congelado" (compilado):

```python
if getattr(sys, 'frozen', False):
    # Executável compilado: usa diretório do .exe
    base_path = Path(sys.executable).parent
else:
    # Desenvolvimento: usa raiz do projeto
    base_path = Path(__file__).resolve().parent.parent
```

## Regras para Adicionar Novas Funcionalidades

### ❌ NUNCA FAÇA ISSO:

```python
# NÃO use caminhos relativos diretos
with open("assets/data.json") as f:
    data = json.load(f)

# NÃO use __file__ diretamente para assets
BASE_DIR = Path(__file__).resolve().parent.parent
file_path = BASE_DIR / "assets" / "file.txt"

# NÃO use os.path.abspath com caminhos relativos
icon_path = os.path.abspath("assets/icons/icon.ico")
```

### ✅ SEMPRE FAÇA ISSO:

```python
from helpers.paths import get_asset_path, get_icon_path

# Para arquivos na pasta assets
data_path = get_asset_path("data", "config.json")
with open(data_path) as f:
    data = json.load(f)

# Para templates de documentos
template = get_asset_path("documents", "template.docx")
output = get_asset_path("documents", "output.pdf")

# Para ícones (retorna string)
icon = get_icon_path("app_icon.ico")
page.window.icon = icon

# Para múltiplos níveis de diretório
deep_file = get_asset_path("images", "logos", "company.png")
# Retorna: base_path/assets/images/logos/company.png
```

## Exemplos Práticos

### Exemplo 1: Lendo um arquivo JSON de configuração

```python
from helpers.paths import get_asset_path
import json

def load_config():
    config_path = get_asset_path("json", "config.json")
    with open(config_path, 'r', encoding='utf-8') as f:
        return json.load(f)
```

### Exemplo 2: Gerando um documento

```python
from helpers.paths import get_asset_path
from docx import Document

def generate_report(customer_name):
    # Template de entrada
    template_path = get_asset_path("documents", "report_template.docx")
    
    # Arquivo de saída
    output_path = get_asset_path("documents", f"{customer_name}_report.docx")
    
    doc = Document(template_path)
    # ... processar documento ...
    doc.save(output_path)
    
    return str(output_path)
```

### Exemplo 3: Carregando uma imagem

```python
from helpers.paths import get_asset_path
from PIL import Image

def load_logo():
    logo_path = get_asset_path("images", "logo.png")
    return Image.open(logo_path)
```

### Exemplo 4: Definindo ícone da janela

```python
from helpers.paths import get_icon_path
import flet as ft

def setup_window(page: ft.Page):
    page.window.icon = get_icon_path("app_icon.ico")
```

## Estrutura de Diretórios

```
MerxWell/
├── assets/
│   ├── documents/      # Templates e documentos gerados
│   ├── icons/          # Ícones da aplicação
│   ├── images/         # Imagens e logos
│   ├── json/           # Arquivos de configuração
│   └── pdfs/           # PDFs gerados
├── helpers/
│   └── paths.py        # ⭐ Módulo de resolução de paths
├── scripts/
│   ├── proposal_generator.py  # Usa get_asset_path()
│   └── save_proposal.py       # Usa get_asset_path()
└── main.py             # Usa get_icon_path()
```

## Checklist para Novas Funcionalidades

Ao adicionar código que acessa arquivos:

- [ ] Importei `get_asset_path` ou `get_icon_path` de `helpers.paths`?
- [ ] Usei a função helper em vez de caminhos hardcoded?
- [ ] Testei em modo desenvolvimento (`python main.py`)?
- [ ] Testei após build (`python setup.py build`)?
- [ ] Os arquivos necessários estão na pasta `assets/`?
- [ ] O `setup.py` inclui a pasta `assets` em `include_files`?

## Troubleshooting

### Erro: "FileNotFoundError" após build

**Causa:** O arquivo não está sendo copiado para o build.

**Solução:** Verifique se a pasta está em `setup.py`:

```python
"include_files": [
    ("assets", "assets"),  # ✅ Copia toda pasta assets
    (".env", ".env"),
]
```

### Erro: "ModuleNotFoundError: No module named 'helpers.paths'"

**Causa:** O módulo helpers não está sendo incluído no build.

**Solução:** Verifique se está em `setup.py`:

```python
"includes": [
    "helpers",  # ✅ Inclui módulo helpers
    "config",
    "screens",
    "scripts",
]
```

### Path retorna local errado

**Debug:** Adicione prints temporários:

```python
from helpers.paths import get_base_path, get_asset_path

print(f"Base path: {get_base_path()}")
print(f"Asset path: {get_asset_path('documents', 'test.docx')}")
```

## Resumo

**Regra de Ouro:** 
> Sempre use `get_asset_path()` para qualquer arquivo dentro de `assets/` e `get_icon_path()` para ícones. Nunca use caminhos relativos diretos ou `__file__` para acessar assets.

Isso garante que seu código funcione perfeitamente tanto durante o desenvolvimento quanto após compilar com cx_Freeze.

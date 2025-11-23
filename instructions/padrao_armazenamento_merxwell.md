# PADRÃO DE ARMAZENAMENTO DE ARQUIVOS EM APLICAÇÕES FLET BUILDADAS COM CX_FREEZE
### Documento Técnico – MerxWell – Para IA Geradora de Código

## 1. Contexto
A aplicação MerxWell, desenvolvida em Python + Flet, gera arquivos DOCX e PDF a partir de templates localizados em:
assets/documents/

No ambiente de desenvolvimento (PyCharm), tanto a leitura quanto a escrita dentro de assets funcionam normalmente.

Após gerar o executável com cx_Freeze, erros começam a ocorrer:
FileNotFoundError
'NoneType' object has no attribute write

Esses erros acontecem porque o EXE não permite gravação dentro da pasta assets embutida no build.

Este documento define um padrão oficial de armazenamento de arquivos para o MerxWell que funciona tanto no ambiente Dev quanto no EXE compilado.

## 2. Problema
As falhas acontecem porque:

✔ Os arquivos de template precisam estar dentro de assets/
❌ Mas arquivos gerados não podem ser salvos dentro de assets/ no EXE

Quando o programa tenta salvar:

assets/documents/algum_arquivo.docx

no EXE, ocorre erro.

## 3. Causa Técnica
Motivos:

1. assets se torna somente leitura no EXE.
2. Caminhos podem apontar para library.zip.
3. python-docx/docx2pdf exigem caminho físico real.

## 4. Solução Proposta
✔ Ler templates de assets/documents/  
❌ Nunca escrever dentro de assets no EXE  
✔ Salvar arquivos em diretório externo escolhido pelo usuário via FolderPicker  
✔ Persistir pasta escolhida em page.client_storage["merx_output_directory"]

## 5. Arquitetura dos Caminhos
get_asset_path → apenas leitura  
get_output_path → apenas escrita  

## 6. Implementação – helpers/paths.py

### get_asset_path
```python
import os, sys

def get_asset_path(*path_parts):
    if getattr(sys, "frozen", False):
        base_dir = os.path.dirname(sys.executable)
    else:
        base_dir = os.path.abspath(".")
    return os.path.join(base_dir, "assets", *path_parts)
```

### get_output_path
```python
def get_output_path(output_dir, *path_parts):
    os.makedirs(output_dir, exist_ok=True)
    return os.path.join(output_dir, *path_parts)
```

## 7. FolderPicker – Primeira Execução
```python
if not page.client_storage.contains_key("merx_output_directory"):
    picker = ft.FilePicker(on_result=select_output_folder)
    page.overlay.append(picker)
    picker.get_directory_path()
```

## 8. Uso nos Geradores de Propostas
```python
arquivo_origem = get_asset_path("documents", "standard_proposal.docx")
output_dir = page.client_storage.get("merx_output_directory")
arquivo_final_docx = get_output_path(output_dir, f"{razao}.docx")
arquivo_final_pdf = get_output_path(output_dir, f"{razao}.pdf")
```

## 9. Checklist para IA
- Criar helpers/paths.py  
- Implementar folder picker  
- Persistir diretório  
- Usar diretório externo para DOCX/PDF  
- Nunca salvar em assets no EXE  

## 10. Resumo Final
✔ Templates em assets  
✔ Escrita em diretório externo  
✔ Solução 100% compatível com Dev e EXE  

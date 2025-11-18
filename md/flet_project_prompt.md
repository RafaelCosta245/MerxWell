# Prompt para Gerador de Código IA - Projeto Flet Python Desktop

Crie um projeto Flet Python para aplicação desktop com a seguinte estrutura e especificações:

## Estrutura do Projeto

```
project/
├── main.py
├── requirements.txt
├── screens/
│   ├── __init__.py
│   ├── home_screen.py
│   └── exemplo_screen.py
├── scripts/
│   ├── __init__.py
│   ├── database.py
│   └── exemplo_script.py
└── config/
    ├── __init__.py
    └── navigation.py
```

## Requisitos Técnicos

### 1. Sistema de Navegação

- Implementar navegação baseada em **Views** do Flet para transições rápidas e fluidas
- Criar um gerenciador de navegação centralizado em `config/navigation.py`
- Facilitar adição de novas telas através de registro simples no gerenciador
- Suportar navegação com histórico (voltar/avançar)

### 2. Estrutura de Telas (screens/)

- Cada tela deve ser uma classe separada que herda de uma classe base
- Componentes UI devem ser criados individualmente como métodos separados
- Permitir fácil posicionamento e edição de cada componente
- Exemplo de estrutura de tela:
  - `build()`: método principal que monta a tela
  - `create_header()`: cria componente de cabeçalho
  - `create_content()`: cria componente de conteúdo
  - `create_footer()`: cria componente de rodapé

### 3. Scripts de Execução (scripts/)

- Pasta para lógica de negócios e tarefas
- Separar completamente da camada de apresentação
- Incluir tratamento de erros apropriado

### 4. Conexões de Banco de Dados

- **Banco Principal (Supabase)**: para operações de leitura e escrita
  - Configurar cliente Supabase em `scripts/database.py`
  - Métodos para CRUD completo
- **Banco Auxiliar**: apenas para leitura
  - Configurar conexão separada no mesmo arquivo
  - Métodos somente para consultas SELECT

### 5. Arquivo Principal (main.py)

- Inicializar aplicação Flet
- Configurar Views e rotas
- Integrar gerenciador de navegação
- Definir configurações da janela (tamanho, título, etc)

### 6. Requirements.txt

Listar todas as dependências necessárias:
- flet
- supabase
- python-dotenv
- [outras bibliotecas necessárias]

**IMPORTANTE: NÃO incluir código para instalação automática das bibliotecas. As dependências serão instaladas manualmente.**

## Padrões de Código

### Componentes Modulares

Cada componente UI deve ser um método separado que retorna um controle Flet:

```python
def create_botao_exemplo(self):
    return ft.ElevatedButton(
        text="Exemplo",
        on_click=self.handle_click
    )
```

### Facilidade de Adição de Telas

O sistema deve permitir adicionar novas telas apenas:

1. Criando arquivo na pasta `screens/`
2. Registrando a rota no gerenciador de navegação
3. Sem necessidade de modificar múltiplos arquivos

### Configurações

- Usar variáveis de ambiente (.env) para credenciais de banco
- Criar arquivo `.env.example` com estrutura necessária

## Características Desejadas

- Código limpo e bem documentado em português
- Type hints quando apropriado
- Tratamento de erros robusto
- Separação clara de responsabilidades
- Arquitetura escalável para crescimento do projeto
- Performance otimizada para navegação fluida

## Exemplo de Uso da Navegação

```python
# Navegar para uma tela
navigation.go("/home")

# Navegar com parâmetros
navigation.go("/detalhes", params={"id": 123})

# Voltar
navigation.back()
```

## Instruções Finais

Gere o código completo para este projeto seguindo todas as especificações acima, priorizando:

- ✅ Simplicidade
- ✅ Modularidade
- ✅ Facilidade de manutenção
- ✅ Navegação fluida com Views
- ✅ Componentes individuais editáveis
- ✅ Fácil adição de novas telas

**Lembre-se: NÃO gerar código de instalação de bibliotecas. Apenas listar no requirements.txt.**
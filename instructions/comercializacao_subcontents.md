# Estrutura de Subconteúdos (sub_content_area) da tela Comercialização

Este documento descreve como a tela **Comercialização** foi estruturada em múltiplos módulos Python, cada um responsável pelo conteúdo de um submenu. A ideia é servir de **modelo** para criar novas subáreas de conteúdo em outras telas do projeto.

## Visão geral

A classe `ComercializacaoScreen` continua sendo o **ponto de entrada** da tela, mas o conteúdo de cada submenu foi extraído para módulos separados em `screens/`:

- `comercializacao_portfolio.py`   → submenu **Portfólio** (`key = "visao"`)
- `comercializacao_visao_geral.py` → submenu **Visão Geral** (`key = "visao_geral"`)
- `comercializacao_fluxos.py`      → submenu **Fluxos** (`key = "fluxos"`)
- `comercializacao_contratos.py`   → submenu **Contratos** (`key = "contratos"`)
- `comercializacao_clientes.py`    → submenu **Clientes** (`key = "clientes"`)
- `comercializacao_produtos.py`    → submenu **Produtos** (`key = "produtos"`)

A responsabilidade de **criar o conteúdo** de cada aba foi movida para funções `create_*_content` nesses módulos. A `ComercializacaoScreen` apenas:

- Lê os parâmetros de navegação (`submenu`, `client`, filtros etc.).
- Decide qual submenu está ativo.
- Chama a função correspondente do módulo.
- Envolve o resultado em um container rolável.

## Padrão dentro de `ComercializacaoScreen`

Arquivo: `screens/comercializacao_screen.py`

### Imports

```python
from screens import (
    comercializacao_contratos,
    comercializacao_portfolio,
    comercializacao_visao_geral,
    comercializacao_fluxos,
    comercializacao_clientes,
    comercializacao_produtos,
)
```

### Seleção do subconteúdo

A lógica de escolha do conteúdo fica centralizada em `_create_subcontent_area`:

```python
def _create_subcontent_area(
    self,
    selected_submenu: str,
    selected_client: Optional[str],
    energy_type: Optional[str],
    submarket: Optional[str],
    contract_type: Optional[str],
    buyer_filter: Optional[str],
    seller_filter: Optional[str],
) -> ft.Control:
    if selected_submenu == "visao":
        inner = comercializacao_portfolio.create_portfolio_content(
            self,
            selected_client,
            energy_type,
            submarket,
            contract_type,
        )
    elif selected_submenu == "visao_geral":
        inner = comercializacao_visao_geral.create_visao_geral_content(self)
    elif selected_submenu == "fluxos":
        inner = comercializacao_fluxos.create_fluxos_content(self)
    elif selected_submenu == "contratos":
        inner = comercializacao_contratos.create_contratos_content(
            self,
            buyer_filter,
            seller_filter,
        )
    elif selected_submenu == "clientes":
        inner = comercializacao_clientes.create_clientes_content(self)
    elif selected_submenu == "produtos":
        inner = comercializacao_produtos.create_produtos_content(self)
    else:
        inner = comercializacao_visao_geral.create_visao_geral_content(self)

    return self._wrap_in_scrollable_area(inner)
```

> Observação: `_wrap_in_scrollable_area` continua em `ComercializacaoScreen` para garantir o mesmo comportamento de scroll para todos os submódulos.

## Padrão de cada módulo de subconteúdo

A seguir, um resumo de como cada módulo foi estruturado. Esse padrão pode ser replicado em novas telas.

### 1. Portfólio – `comercializacao_portfolio.py`

Responsável pela antiga função `_create_visao_dashboard` (dashboard por cliente com filtros e gráficos).

Padrão de função pública:

```python
def create_portfolio_content(
    screen: Any,
    selected_client: Optional[str],
    energy_type: Optional[str],
    submarket: Optional[str],
    contract_type: Optional[str],
) -> ft.Control:
    ...  # monta todo o conteúdo
```

Características:

- O módulo importa diretamente `get_client_dashboard_data`, `list_contract_clients` e `MONTH_LABELS`.
- Helpers internos (não exportados):
  - `_create_filters_row(...)` → monta filtros e usa `screen.navigation.go(...)` dentro do `on_change`.
  - `_create_metric_summary(...)` e `_create_empty_metrics_row()` → cards de métricas.
  - `_create_year_chart_card(...)` e `_create_year_charts(...)` → gráficos em MWm, barras de compra/venda/diferença e legendas com preços médios.

### 2. Visão Geral – `comercializacao_visao_geral.py`

Responsável pela antiga `_create_dashboard_content` e seus cards.

```python
def create_visao_geral_content(screen: Any) -> ft.Control:
    # monta os dois rows de cards reutilizando _create_metric_card
```

- Helpers internos: `_create_metric_card(...)`.
- Não precisa de navegação, então o `screen` só é passado por consistência de assinatura.

### 3. Fluxos – `comercializacao_fluxos.py`

Responsável pela antiga `_create_fluxos_content`.

```python
def create_fluxos_content(screen: Any) -> ft.Control:
    # monta grid de cards usando _create_fluxo_chart_card
```

- Helper interno: `_create_fluxo_chart_card(row_index, col_index)`.

### 4. Contratos – `comercializacao_contratos.py`

Responsável pela antiga `_create_contratos_content`, `_create_contracts_table` e `_format_date`.

```python
def create_contratos_content(
    screen: Any,
    buyer_filter: Optional[str],
    seller_filter: Optional[str],
) -> ft.Control:
    ...
```

Principais pontos:

- Lê os filtros (`buyer_filter`, `seller_filter`) vindos da navegação e aplica filtragem em memória sobre `list_contracts_for_table()`.
- Campos de busca:
  - `TextField` para Comprador e Vendedor.
  - `on_submit` dos dois chama `apply_filters`, que faz `screen.navigation.go("/comercializacao", params={...})`.
- Botões:
  - `Pesquisar` e `Novo Contrato` lado a lado, com mesmo `width`/`height`.
- Tabela:
  - Implementada em `_create_contracts_table(contracts)` usando containers, linhas alternadas e botões de ação com ícones pretos.
- Helper de data: `_format_date(value)`.

### 5. Clientes – `comercializacao_clientes.py`

Responsável pelo conteúdo placeholder para `Clientes`.

```python
def create_clientes_content(screen: Any) -> ft.Control:
    # container simples com título e descrição
```

### 6. Produtos – `comercializacao_produtos.py`

Responsável pelo conteúdo placeholder para `Produtos`.

```python
def create_produtos_content(screen: Any) -> ft.Control:
    # container simples com título e descrição
```

## Como reutilizar esse padrão em outras telas

Para criar uma nova tela com submenus estruturados da mesma forma:

1. **Defina a screen principal** (por exemplo, `FinanceiroScreen`) com:
   - Coluna de submenus.
   - Leitura de parâmetros de navegação (`submenu`, filtros específicos).
   - Função `_create_subcontent_area(...)` que só decide **qual módulo chamar**.

2. **Crie um módulo por submenu** em `screens/`, seguindo a convenção:

   - `financeiro_fluxos.py` → `create_fluxos_content(screen, ...)`
   - `financeiro_relatorios.py` → `create_relatorios_content(screen, ...)`
   - etc.

3. **Assinatura das funções de conteúdo:**

   - Sempre receba `screen: Any` como primeiro argumento para poder usar:

     ```python
     screen.navigation.go("/rota", params={...})
     ```

   - Demais parâmetros devem refletir os filtros/estado que vêm de `create_content`.

4. **Helpers locais:**

   - Funções auxiliares que só fazem sentido dentro de um submenu (formatação, pequenas tabelas, componentes específicos) devem ficar **dentro do módulo** desse submenu, com nome iniciado por `_` para indicar uso interno.

5. **Scroll e layout geral:**

   - Deixe o comportamento de scroll padronizado na screen principal, como em `ComercializacaoScreen._wrap_in_scrollable_area`, para que todos os submódulos tenham o mesmo tratamento de rolagem.

## Benefícios dessa estrutura

- **Separação de responsabilidades:** cada arquivo trata de um contexto/coordenador de UI mais específico.
- **Leitura mais simples:** para ajustar a aba de contratos, basta abrir `comercializacao_contratos.py`.
- **Reaproveitamento de padrão:** facilita criar novas telas com submenus usando o mesmo modelo de delegação.

Este padrão deve ser seguido sempre que uma screen tiver múltiplos submenus com conteúdos relativamente grandes ou complexos.

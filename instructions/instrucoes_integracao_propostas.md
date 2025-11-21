# 🧩 Instruções Claras para IA — Integração do Formulário de Propostas com o Banco de Dados (Supabase)

Este documento descreve de forma **objetiva, explícita e sem ambiguidade** como uma IA geradora de código deve implementar a **persistência dos dados do formulário** de Nova Proposta Comercial no banco de dados **Supabase (PostgreSQL)**.

As instruções garantem que a IA **não erre a integração**, seguindo exatamente:
- A estrutura do formulário existente no arquivo `comercializacao_nova_proposta.py` (referência interna do projeto).
- As tabelas SQL criadas: `proposals` e `proposal_seasonalities`.

---

# ✅ 1. Estruturas das Tabelas no Banco de Dados

## **1.1 Tabela `proposals`** (principal)
A proposta deve ser salva primeiro nesta tabela.

| Campo | Tipo | Obrigatório | Origem no Formulário |
|-------|------|-------------|------------------------|
| id | uuid | gerado pelo banco | — |
| customer_cnpj | text | sim | campo CNPJ |
| customer_name | text | sim | campo Razão Social |
| submarket | text | sim | dropdown Submercado |
| energy_type | text | sim | dropdown Tipo de energia |
| supply_start | date | sim | campo Início Suprimento |
| supply_end | date | sim | campo Fim Suprimento |
| modulation | text | não | dropdown Modulação |
| billing_due_day | integer | não | campo Data de Pagamento (dia útil) |
| guarantee_type | text | não | dropdown Garantia |
| guarantee_months | integer | não | campo Qty_meses |
| reference_date | text | não | campo Data Base |
| proposal_validity | text | não | campo Validade da Proposta |
| status | text | default 'PENDING' | — |
| converted_to_contract | boolean | default false | — |
| contract_id | uuid | null | — |
| created_at | timestamptz | gerado | — |
| updated_at | timestamptz | gerado | — |

---

## **1.2 Tabela `proposal_seasonalities`** (tabela filha — 1 para cada ano)
Cada ano selecionado no formulário gera **uma linha** nesta tabela.

| Campo | Tipo | Origem no Formulário |
|--------|------|----------------------|
| id | uuid | gerado |
| proposal_id | uuid | ID da proposta criada |
| year | integer | inferido pelas datas início/fim |
| price | numeric | campo "Preço" |
| flex | numeric | campo "Flex" |
| seasonality | numeric | campo "Sazo" |
| average_volume | numeric | campo "Vol" |
| is_flat | boolean | campo "Flat" |
| january — december | numeric | valores mensais da tabela |

---

# 🧩 2. Relação entre Formulário e Banco

A partir deste ponto, **a tabela `proposal_logs` passa a fazer parte oficial da integração** e deve ser utilizada para registrar eventos importantes do processo.

A IA deve entender que o formulário possui **3 seções**:

### **Seção 1 – Dados Gerais** → Grava diretamente em `proposals`.
### **Seção 2 – Condições Comerciais** → Grava 1 registro por ano em `proposal_seasonalities`.
### **Seção 3 – Dados Complementares** → Também grava em `proposals`.

Todo o relacionamento é:
```
proposals (1) ──▶ (N) proposal_seasonalities
```

---

# 🚀 3. Regras Obrigatórias de Salvamento

## **3.1 Passo 1 — Salvar Proposta em `proposals`**
A IA deve:
1. Ler todos os campos da aba **Dados Gerais**.
2. Ler todos os campos da aba **Dados Complementares**.
3. Converter datas no formato brasileiro `DD/MM/YYYY` para `YYYY-MM-DD`.
4. Enviar esses dados como **um único insert** para a tabela `proposals`.
5. Receber o `id` gerado pela tabela.

### ❗ Não prosseguir para sazonalidade sem o ID da proposta.

---

## **3.2 Passo 2 — Identificar os anos da sazonalidade**
A IA deve:
- Usar as datas `supply_start` e `supply_end`.
- Extrair os anos: todos entre início e fim.

Exemplo:  
```
Início: 01/01/2026  
Fim: 31/12/2029  
Anos: 2026, 2027, 2028, 2029
```

Esses são os anos que devem ser salvos em `proposal_seasonalities`.

---

## **3.3 Passo 3 — Salvar Condições Comerciais em `proposal_seasonalities`**
Para cada ano:
1. Criar um registro.
2. Vincular ao `proposal_id` retornado no passo 1.
3. Ler os campos correspondentes no formulário, incluindo:
   - price
   - flex
   - seasonality
   - average_volume
   - is_flat
   - monthly volumes: january … december
4. Converter vírgulas para ponto antes de salvar.

### ❗ Cada ano = um insert separado.

---

# 🔒 4. Regras Obrigatórias de Validação
A IA deve garantir que:

### **4.1 CNPJ deve ser salvo sem máscara**
Remover:
```
., -, /
```

### **4.2 Datas devem ser convertidas**  
De:
```
DD/MM/YYYY
```
Para:
```
YYYY-MM-DD
```

### **4.3 Meses vazios devem ser salvos como `NULL`**
Nunca salvar string vazia.

### **4.4 Campos numéricos devem usar ponto decimal**
```
12,50 → 12.50
```

---

# 🧱 5. Exemplo de JSON que a IA deve construir para envio ao Supabase

```json
{
  "customer_cnpj": "12345678000123",
  "customer_name": "Empresa Exemplo SA",
  "submarket": "NE",
  "energy_type": "I5",
  "supply_start": "2026-01-01",
  "supply_end": "2028-12-31",
  "modulation": "FLAT",
  "billing_due_day": 6,
  "guarantee_type": "Insurance",
  "guarantee_months": 2,
  "reference_date": "01/2026",
  "proposal_validity": "10/12/2025 18:00"
}
```

E as sazonalidades:

```json
[
  {
    "year": 2026,
    "price": 312.55,
    "flex": 10,
    "seasonality": 5,
    "average_volume": 1.2,
    "is_flat": true,
    "january": 800,
    "february": 760,
    ...
  },
  {
    "year": 2027,
    ...
  }
]
```

---

# 📤 6. Fluxo Completo que a IA Deve Executar

## **Etapa 1 — Inserir na tabela `proposals`**
- Montar JSON com todos os campos exceto sazonalidade.
- Executar `insert` no Supabase.
- Guardar o `proposal_id` retornado.

## **Etapa 2 — Inserir sazonalidade para cada ano**
- Para cada ano:
  - montar payload JSON com os dados daquele ano
  - incluir `proposal_id`
  - executar insert em `proposal_seasonalities`

## **Etapa 3 — Retornar sucesso para o aplicativo**
- Não retornar dados sensíveis
- Retornar apenas:
```
{ "success": true, "proposal_id": "..." }
```

---

# 🧱 6. Integração com `proposal_logs`

A IA deve registrar logs **após cada etapa crítica**:

## **6.1 Log obrigatório ao criar proposta**
Após inserir na tabela `proposals`, a IA deve executar:
```sql
insert into proposal_logs (proposal_id, message)
values (<PROPOSAL_ID>, 'Proposal created successfully');
```

## **6.2 Log obrigatório após salvar TODAS as sazonalidades**
```sql
insert into proposal_logs (proposal_id, message)
values (<PROPOSAL_ID>, 'All seasonalities saved successfully');
```

## **6.3 Log obrigatório em caso de erro**
Em caso de erro na integração, gerar log com:
```sql
insert into proposal_logs (proposal_id, message)
values (<PROPOSAL_ID>, 'Error: <DESCRIÇÃO DO ERRO>');
```

### Regras do módulo de logs
- Nunca impedir o fluxo principal caso o log falhe.
- Nunca criar log antes de `proposal_id` existir.
- Mensagens devem ser claras e descritivas.

---

# 🛑 Ordem obrigatória (a IA *não pode* alterar)
1. Validar dados
2. Salvar proposta
3. Obter ID
4. Salvar sazonalidades (cada ano separadamente)
5. Retornar conclusão

---

# 🧭 7. Proibições (a IA nunca deve fazer)

❌ Não salvar sazonalidade antes de criar a proposta  
❌ Não ignorar campos de meses  
❌ Não salvar string vazia em campos numéricos  
❌ Não salvar datas sem converter  
❌ Não deixar vírgulas como separador decimal  
❌ Não tentar atualizar contrato se `contract_id` for null  
❌ Não criar novas tabelas ou campos

---

# 🏁 8. Resultado Esperado

Após seguir este documento, a IA será capaz de:
- Mapear corretamente os campos do formulário
- Criar proposta no banco Supabase
- Criar sazonalidades vinculadas por ano
- Garantir consistência e integridade de dados
- Preparar tudo para futura geração de contratos

---

Se for necessário, podemos incluir:
- Exemplos de queries SQL
- Exemplos de código Supabase para TS/Python
- Exemplo de endpoint REST
- Modelo OpenAPI

Só pedir!


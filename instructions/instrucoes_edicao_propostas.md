# 📝 Instruções Claras — Edição de uma Proposta Existente (Supabase / PostgreSQL)

Este documento descreve **de forma explícita, segura e sem margem para erro** como uma IA geradora de código deve executar a **edição de uma proposta já existente** no banco de dados Supabase/PostgreSQL.

A operação de edição deve sempre:
- manter integridade referencial,
- atualizar somente os campos desejados,
- preservar dados não alterados,
- garantir logs obrigatórios antes e depois da modificação,
- atualizar sazonalidades corretamente quando aplicável.

---

# ✅ 1. Tabelas Envolvidas
A edição de uma proposta envolve até **três tabelas**:

### ✔ `proposals` (tabela principal)
Campos gerais e complementares da proposta.

### ✔ `proposal_seasonalities` (filha — 1:N)
Somente deve ser alterada caso haja mudança em preço, flex, volume, sazonalidade ou meses.

### ✔ `proposal_logs` (filha — 1:N)
Não deve ser modificada diretamente — somente criar novos logs para registrar a edição.

### ✔ `audit_events` (tabela externa)
Necessária para armazenar logs permanentes da edição.

---

# 🧭 2. Fluxo Obrigatório da IA
A IA deve seguir **exatamente esta ordem**:

---
## **Etapa 1 — Validar o ID da Proposta**
A IA deve confirmar que o ID existe:

```sql
select id from proposals where id = <PROPOSAL_ID>;
```

Se não existir:
- retornar erro **"Proposal not found"**
- interromper operação

---

## **Etapa 2 — Criar LOG OBRIGATÓRIO de início de edição**
O log deve ser gravado em `audit_events`.

```sql
insert into audit_events (event_type, reference_id, description)
values (
  'proposal_edit_requested',
  <PROPOSAL_ID>,
  'Edition process initiated for proposal'
);
```

Se este log falhar → cancelar a edição.

---

# 🛠 3. Atualização da Proposta (Tabela `proposals`)
A IA deve atualizar somente os campos enviados e deixar todos os demais inalterados.

## **Regras obrigatórias:**
- Nunca sobrescrever campo com valor vazio.
- Sempre validar datas e converter para `YYYY-MM-DD`.
- Sempre remover máscara do CNPJ.
- Não alterar `id`, `created_at`, `contract_id` ou `converted_to_contract`.

## **Exemplo de atualização parcial:**
```sql
update proposals
set
  customer_name = <NOVO_NOME>,
  submarket = <NOVO_SUBMERCADO>,
  energy_type = <NOVO_TIPO>,
  updated_at = now()
where id = <PROPOSAL_ID>;
```

A IA deve **somente** incluir no `SET` os campos que forem informados.

---

# 📊 4. Atualização das Sazonalidades (Tabela `proposal_seasonalities`)
Esta etapa só deve ser executada **se os dados de condições comerciais forem enviados**.

### A IA deve seguir as seguintes regras:
1. Cada ano deve ser identificado pelo campo `year`.
2. Somente os anos enviados devem ser atualizados.
3. Campos não enviados não devem ser modificados.
4. Valores numéricos devem substituir vírgulas por ponto.
5. Meses vazios devem ser salvos como NULL.
6. Caso um ano não exista na tabela, a IA deve registrar erro.

---

## **Exemplo de atualização de sazonalidade:**
```sql
update proposal_seasonalities
set
  price = <NOVO_PRECO>,
  flex = <NOVO_FLEX>,
  seasonality = <NOVA_SAZO>,
  average_volume = <NOVO_VOLUME>,
  january = <NOVO_JAN>,
  february = <NOVO_FEV>,
  ...
  updated_at = now()
where proposal_id = <PROPOSAL_ID>
  and year = <ANO_REFERENCIA>;
```

A IA **não deve apagar** sazonalidades existentes durante edição.

---

# 🧱 5. Logs OBRIGATÓRIOS Pós-Edição
Após concluir a atualização, a IA deve registrar:

```sql
insert into audit_events (event_type, reference_id, description)
values (
  'proposal_edited',
  <PROPOSAL_ID>,
  'Proposal updated successfully'
);
```

Este log é obrigatório.

---

# 🛑 6. Regras de Segurança — A IA NUNCA deve:

❌ Sobrescrever dados não enviados

❌ Criar novos registros de sazonalidade durante edição

❌ Deletar registros de sazonalidade existentes

❌ Atualizar `id`, `created_at` ou `contract_id`

❌ Registrar logs na tabela `proposal_logs`

❌ Editar uma proposta que já foi convertida em contrato (`converted_to_contract = true`)

❌ Continuar sem registrar logs iniciais e finais

---

# 🚀 7. Fluxo SQL Consolidado — Exemplo

```sql
-- 1. Validar existência\select id from proposals where id = 'UUID_PROPOSTA';

-- 2. Log inicial
insert into audit_events (event_type, reference_id, description)
values ('proposal_edit_requested', 'UUID_PROPOSTA', 'Edition process initiated for proposal');

-- 3. Atualizar dados da proposta
update proposals
set
  customer_name = 'Novo Nome',
  submarket = 'NE',
  energy_type = 'I5',
  updated_at = now()
where id = 'UUID_PROPOSTA';

-- 4. Atualizar sazonalidade (se enviado)
update proposal_seasonalities
set price = 300.25, updated_at = now()
where proposal_id = 'UUID_PROPOSTA' and year = 2027;

-- 5. Log final
insert into audit_events (event_type, reference_id, description)
values ('proposal_edited', 'UUID_PROPOSTA', 'Proposal updated successfully');
```

---

# 🏁 8. Resultado Final
Após seguir estas instruções, a IA garantirá que:

- A edição é feita com segurança
- Apenas campos informados serão modificados
- A sazonalidade será atualizada corretamente
- Logs permanentes serão criados
- A integridade dos dados permanece garantida

---



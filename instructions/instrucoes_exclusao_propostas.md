# 🧨 Instruções Claras — Exclusão Completa de uma Proposta (Supabase / PostgreSQL)

Este documento fornece instruções **definitivas e obrigatórias** para que uma IA geradora de código execute a **exclusão completa** de uma proposta no banco de dados Supabase, **com segurança, integridade e logs obrigatórios** do processo.

A operação deve remover:
- o registro principal da proposta,
- todas as sazonalidades vinculadas,
- todos os logs internos vinculados,
- e registrar logs permanentes da exclusão em uma tabela externa.

Nenhuma tabela será apagada — somente **registros**.

---

# ✅ 1. Tabelas Envolvidas
A exclusão completa envolve **três tabelas diretamente** e **uma tabela externa para auditoria**.

### **1. proposals** (tabela principal)
Registro da proposta.

### **2. proposal_seasonalities** (filha – 1:N)
Volumes anuais e mensais.

### **3. proposal_logs** (filha – 1:N)
Logs internos da proposta.

### **4. audit_events** (tabela externa)
Registro permanente da exclusão.

As tabelas filhas possuem:
```sql
ON DELETE CASCADE
```
Portanto, ao deletar a proposta, **todos os registros relacionados serão removidos automaticamente**.

---

# 🧨 2. Regra Fundamental da Exclusão
A exclusão só deve ocorrer usando **apenas**:
```sql
delete from proposals where id = <PROPOSAL_ID>;
```

Nunca realizar deletes diretos em:
- `proposal_seasonalities`
- `proposal_logs`

O mecanismo de cascata cuida disso automaticamente.

---

# 🧭 3. Fluxo Obrigatório da IA
A IA deve seguir **exclusivamente** os passos abaixo, na ordem correta.

---
## **Etapa 1 — Validar o ID da proposta**
A IA deve verificar:
- ID fornecido
- formato UUID válido
- existência do registro

Consulta obrigatória:
```sql
select id from proposals where id = <PROPOSAL_ID>;
```

Se o registro **não existir**:
- retornar erro **"Proposal not found"**
- **cancelar o processo**

---
## **Etapa 2 — Criar LOG OBRIGATÓRIO de início da exclusão**
Este log deve ser gravado **ANTES** da exclusão, obrigatoriamente na tabela `audit_events`.

```sql
insert into audit_events (event_type, reference_id, description)
values (
  'proposal_delete_requested',
  <PROPOSAL_ID>,
  'Deletion process initiated for proposal'
);
```

Se este log falhar:
- a exclusão deve ser cancelada

---
## **Etapa 3 — Excluir a proposta**
Comando único permitido:

```sql
delete from proposals where id = <PROPOSAL_ID>;
```

Deixar que o banco remova automaticamente:
- sazonalidades (`proposal_seasonalities`)
- logs internos (`proposal_logs`)

### **Proibições absolutas:**
- ❌ Não deletar manualmente tabelas filhas
- ❌ Não alterar keys ou cascades
- ❌ Não executar exclusão parcial
- ❌ Não deletar múltiplas propostas em lote

---
## **Etapa 4 — Verificar se a exclusão ocorreu**
A IA deve executar:
```sql
select count(*) from proposals where id = <PROPOSAL_ID>;
```

Se o resultado for:
- `0` → exclusão confirmada
- `>=1` → erro crítico, abortar processo e registrar falha

---
## **Etapa 5 — Criar LOG OBRIGATÓRIO de conclusão**
Após a confirmação da exclusão:
```sql
insert into audit_events (event_type, reference_id, description)
values (
  'proposal_deleted',
  <PROPOSAL_ID>,
  'Proposal and all related records deleted successfully'
);
```

Este log é **obrigatório** e confirma auditoria permanente.

---

# 🛑 4. Regras de Segurança — A IA NUNCA pode:

❌ Excluir registros diretamente de `proposal_seasonalities`

❌ Excluir registros diretamente de `proposal_logs`

❌ Excluir mais de uma proposta ao mesmo tempo

❌ Executar delete sem log inicial

❌ Prosseguir sem validar a existência do ID

❌ Modificar relacionamentos ou desativar cascades

❌ Realizar exclusão parcial (sempre total)

---

# 🔥 5. Fluxo SQL Consolidado (Exemplo Completo)

```sql
-- 1. Validar existência
select id from proposals where id = 'UUID_AQUI';

-- 2. Log inicial
insert into audit_events (event_type, reference_id, description)
values (
  'proposal_delete_requested',
  'UUID_AQUI',
  'Deletion process initiated for proposal'
);

-- 3. Excluir proposta (cascade remove filhos)
delete from proposals where id = 'UUID_AQUI';

-- 4. Confirmar exclusão
select count(*) from proposals where id = 'UUID_AQUI';

-- 5. Log final
insert into audit_events (event_type, reference_id, description)
values (
  'proposal_deleted',
  'UUID_AQUI',
  'Proposal and all related records deleted successfully'
);
```

---

# 🏁 6. Resultado Final
Após seguir este documento, a IA garantirá:

- remoção completa da proposta,
- remoção automática das sazonalidades,
- remoção automática dos logs internos,
- criação de logs permanentes de auditoria,
- zero risco de inconsistência,
- integridade total do banco de dados.

---


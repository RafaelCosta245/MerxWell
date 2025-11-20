# 📥 Guia de Inserção de Preços de Energia no Banco de Dados

Este documento descreve o processo completo de inserção dos dados de preços de energia extraídos do arquivo Excel no banco de dados Supabase (PostgreSQL).

---

## 🎯 Objetivo

Inserir os preços de energia obtidos do dicionário `precos` (gerado pelo script `take_srn_foward.py`) nas tabelas `energy_price_snapshots` e `energy_prices`.

---

## 📊 Estrutura do Dicionário de Origem

O script Python gera um dicionário com a seguinte estrutura:

```python
precos = {
    'I5': {
        'NORDESTE': {2027: 150.50, 2028: 155.30, ...},
        'NORTE': {2027: 148.20, 2028: 152.10, ...},
        'SUL': {2027: 160.00, 2028: 165.50, ...},
        'SUDESTE': {2027: 158.75, 2028: 163.25, ...}
    },
    'I1': {
        'NORDESTE': {2027: 140.00, ...},
        ...
    },
    'CQ5': {
        ...
    },
    'CONVENCIONAL': {
        ...
    }
}
```

**Estrutura**: `precos[tipo_energia][submercado][ano] = preco`

---

## 🗄️ Estrutura das Tabelas de Destino

### Tabela: `energy_price_snapshots`
Armazena o registro de quando os preços foram capturados.

| Coluna         | Tipo      | Descrição                                    |
|----------------|-----------|----------------------------------------------|
| id             | UUID      | ID único (gerado automaticamente)            |
| trader_id      | UUID      | ID da comercializadora (FK para traders)     |
| snapshot_date  | DATE      | Data da captura dos preços                   |
| created_at     | TIMESTAMP | Data de criação do registro                  |
| updated_at     | TIMESTAMP | Data da última atualização                   |

### Tabela: `energy_prices`
Armazena cada preço individual.

| Coluna       | Tipo         | Descrição                                      |
|--------------|--------------|------------------------------------------------|
| id           | UUID         | ID único (gerado automaticamente)              |
| snapshot_id  | UUID         | ID do snapshot (FK para energy_price_snapshots)|
| year         | INTEGER      | Ano do preço (ex: 2027)                        |
| energy_type  | VARCHAR(20)  | Tipo de energia ('I5', 'I1', 'CQ5', etc.)      |
| submarket    | VARCHAR(20)  | Submercado ('NORDESTE', 'NORTE', etc.)         |
| price        | DECIMAL(12,4)| Valor do preço                                 |
| created_at   | TIMESTAMP    | Data de criação do registro                    |

---

## 🔄 Fluxo de Inserção

### Passo 1: Criar o Snapshot
Antes de inserir os preços, crie um registro na tabela `energy_price_snapshots`:

```sql
INSERT INTO energy_price_snapshots (trader_id, snapshot_date)
VALUES ('uuid-da-comercializadora', CURRENT_DATE)
RETURNING id;
```

**Importante**: 
- O `trader_id` deve ser um UUID válido existente na tabela `traders`
- O `snapshot_date` normalmente é a data atual (`CURRENT_DATE`)
- Guarde o `id` retornado para usar nas inserções de preços

### Passo 2: Inserir os Preços
Para cada combinação de tipo_energia → submercado → ano → preço no dicionário:

```sql
INSERT INTO energy_prices (snapshot_id, year, energy_type, submarket, price)
VALUES 
    ('snapshot-id-do-passo-1', 2027, 'I5', 'NORDESTE', 150.50),
    ('snapshot-id-do-passo-1', 2027, 'I5', 'NORTE', 148.20),
    ... (continua para todos os registros)
;
```

---

## 💻 Exemplo de Implementação em Python

### Código Completo

```python
import pandas as pd
import tkinter as tk
from tkinter import filedialog
from supabase import create_client, Client
from datetime import date
from typing import Dict

# ============================================
# CONFIGURAÇÃO DO SUPABASE
# ============================================
SUPABASE_URL = "sua-url-do-supabase"
SUPABASE_KEY = "sua-chave-do-supabase"
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

# ============================================
# CONFIGURAÇÃO
# ============================================
TRADER_ID = "uuid-da-comercializadora"  # Substitua pelo ID real

# ============================================
# 1. CARREGAR DADOS DA PLANILHA
# ============================================
root = tk.Tk()
root.withdraw()

caminho_arquivo = filedialog.askopenfilename(
    title="Selecione a planilha de preços",
    filetypes=[("Excel Files", "*.xlsx *.xls")]
)

if not caminho_arquivo:
    raise Exception("Nenhum arquivo selecionado!")

df = pd.read_excel(caminho_arquivo)

# ============================================
# 2. CONSTRUIR DICIONÁRIO DE PREÇOS
# ============================================
precos = {}

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

print("✅ Dados carregados com sucesso!")
print(f"📊 Total de tipos de energia: {len(precos)}")

# ============================================
# 3. CRIAR SNAPSHOT NO BANCO
# ============================================
snapshot_data = {
    "trader_id": TRADER_ID,
    "snapshot_date": date.today().isoformat()
}

response = supabase.table("energy_price_snapshots").insert(snapshot_data).execute()

if not response.data:
    raise Exception("❌ Erro ao criar snapshot!")

snapshot_id = response.data[0]["id"]
print(f"✅ Snapshot criado com ID: {snapshot_id}")

# ============================================
# 4. PREPARAR DADOS PARA INSERÇÃO EM LOTE
# ============================================
prices_to_insert = []

for energy_type, submarkets in precos.items():
    for submarket, years in submarkets.items():
        for year, price in years.items():
            prices_to_insert.append({
                "snapshot_id": snapshot_id,
                "year": year,
                "energy_type": energy_type,
                "submarket": submarket,
                "price": price
            })

print(f"📦 Total de preços a inserir: {len(prices_to_insert)}")

# ============================================
# 5. INSERIR PREÇOS EM LOTES
# ============================================
BATCH_SIZE = 1000  # Supabase tem limite de ~1000 registros por request

total_inserted = 0
for i in range(0, len(prices_to_insert), BATCH_SIZE):
    batch = prices_to_insert[i:i + BATCH_SIZE]
    
    response = supabase.table("energy_prices").insert(batch).execute()
    
    if not response.data:
        print(f"⚠️ Erro ao inserir lote {i // BATCH_SIZE + 1}")
        continue
    
    total_inserted += len(response.data)
    print(f"✅ Lote {i // BATCH_SIZE + 1} inserido ({len(response.data)} registros)")

print(f"\n🎉 Inserção concluída! Total: {total_inserted} preços inseridos.")

# ============================================
# 6. VALIDAÇÃO (OPCIONAL)
# ============================================
# Verifica um preço específico
test_query = supabase.table("energy_prices") \
    .select("*") \
    .eq("snapshot_id", snapshot_id) \
    .eq("year", 2027) \
    .eq("energy_type", "I5") \
    .eq("submarket", "NORDESTE") \
    .execute()

if test_query.data:
    print(f"\n✅ Validação: Preço I5 NORDESTE 2027 = {test_query.data[0]['price']}")
else:
    print("\n⚠️ Validação falhou!")
```

---

## 🔧 Detalhes de Implementação

### 1. Instalação de Dependências

```bash
pip install supabase pandas openpyxl tkinter
```

### 2. Obter Credenciais do Supabase

1. Acesse seu projeto no Supabase
2. Vá em **Settings** → **API**
3. Copie:
   - **URL** (Project URL)
   - **anon/public key** (API Key)

### 3. Obter o trader_id

Execute no SQL Editor do Supabase:

```sql
SELECT id, name FROM traders;
```

Copie o UUID da comercializadora desejada.

---

## ⚠️ Tratamento de Erros

### Erro: "duplicate key value violates unique constraint"

**Causa**: Já existe um snapshot para o mesmo trader_id na mesma data.

**Solução 1 - Verificar antes de inserir**:
```python
# Antes de criar o snapshot, verifique se já existe
existing = supabase.table("energy_price_snapshots") \
    .select("id") \
    .eq("trader_id", TRADER_ID) \
    .eq("snapshot_date", date.today().isoformat()) \
    .execute()

if existing.data:
    snapshot_id = existing.data[0]["id"]
    print(f"⚠️ Snapshot já existe. Usando ID: {snapshot_id}")
else:
    # Cria novo snapshot
    ...
```

**Solução 2 - Usar UPSERT**:
```python
response = supabase.table("energy_price_snapshots") \
    .upsert(snapshot_data, on_conflict="trader_id,snapshot_date") \
    .execute()
```

### Erro: Foreign key violation (trader_id)

**Causa**: O UUID do trader não existe na tabela `traders`.

**Solução**: Verifique se o trader existe:
```python
trader = supabase.table("traders").select("id").eq("id", TRADER_ID).execute()
if not trader.data:
    raise Exception(f"Trader {TRADER_ID} não encontrado!")
```

---

## 📈 Consultas Úteis Após Inserção

### Verificar total de preços inseridos
```sql
SELECT COUNT(*) 
FROM energy_prices ep
JOIN energy_price_snapshots eps ON ep.snapshot_id = eps.id
WHERE eps.snapshot_date = CURRENT_DATE;
```

### Ver últimos snapshots
```sql
SELECT eps.snapshot_date, t.name, COUNT(ep.id) as total_prices
FROM energy_price_snapshots eps
JOIN traders t ON eps.trader_id = t.id
LEFT JOIN energy_prices ep ON ep.snapshot_id = eps.id
GROUP BY eps.id, eps.snapshot_date, t.name
ORDER BY eps.snapshot_date DESC
LIMIT 10;
```

### Obter preço específico (mais recente)
```sql
SELECT ep.price, eps.snapshot_date
FROM energy_prices ep
JOIN energy_price_snapshots eps ON ep.snapshot_id = eps.id
WHERE eps.trader_id = 'uuid-do-trader'
  AND ep.year = 2027
  AND ep.energy_type = 'I5'
  AND ep.submarket = 'NORDESTE'
ORDER BY eps.snapshot_date DESC
LIMIT 1;
```

---

## 🎯 Checklist de Execução

- [ ] Instalar dependências Python
- [ ] Configurar credenciais do Supabase
- [ ] Obter UUID do trader correto
- [ ] Executar script Python
- [ ] Verificar snapshot criado
- [ ] Validar quantidade de preços inseridos
- [ ] Testar consulta de preço específico

---

## 📝 Notas Importantes

1. **Unicidade**: A constraint `UNIQUE(trader_id, snapshot_date)` impede múltiplos snapshots no mesmo dia para o mesmo trader. Se precisar atualizar preços no mesmo dia, delete o snapshot anterior ou use UPSERT.

2. **Performance**: Inserções em lote (batch) são muito mais rápidas que inserções individuais.

3. **Transações**: Para garantir atomicidade, considere usar transações se o Supabase SDK suportar.

4. **Dados históricos**: Cada snapshot preserva o histórico. Nunca delete snapshots antigos se quiser manter o histórico de preços.

5. **Formato de data**: Use ISO 8601 (`YYYY-MM-DD`) para compatibilidade.

---

## 🚀 Próximos Passos

Após a inserção bem-sucedida:
1. Criar endpoints de API para consultar preços
2. Implementar gráficos de visualização
3. Criar rotina automatizada de atualização diária
4. Implementar sistema de alertas para variações significativas de preço
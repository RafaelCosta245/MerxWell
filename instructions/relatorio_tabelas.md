# 📄 Mini Relatório das Tabelas – Banco PostgreSQL (Prisma ORM)

Este documento apresenta um resumo técnico das tabelas **Contract**, **ContractSeasonality** e **Trader**, com explicação detalhada das colunas e relacionamentos entre elas.

---

# 🟦 1. Tabela `contracts` (model Contract)

Armazena informações gerais sobre os **contratos de energia** firmados com clientes e comercializadoras.  
É uma das tabelas centrais do sistema.

## 🔑 Chave Primária

- **id** (String, uuid) — Identificador único do contrato.

## 📝 Descrição das Colunas

| Coluna                     | Tipo                  | Descrição                                             |
| -------------------------- | --------------------- | ----------------------------------------------------- |
| service_provider           | String                | Prestador de serviço ou fornecedor de energia.        |
| contractor                 | String                | Empresa contratante (cliente).                        |
| contract_type              | Enum ContractType     | Tipo do contrato (ATACADISTA, VAREJISTA etc.).        |
| contract_code              | String                | Código único que identifica o contrato.               |
| energy_source_type         | Enum EnergySourceType | Tipo da fonte de energia (CONVENCIONAL, I5, I1, CQ5). |
| submarket                  | String                | Submercado (NORTE, NORDESTE, SUL, SUDESTE).           |
| contract_start_date        | DateTime              | Data inicial de vigência.                             |
| contract_end_date          | DateTime              | Data final de vigência.                               |
| power_load_factor          | Float                 | Fator de carga contratado.                            |
| flex_max                   | Float                 | Flexibilidade máxima.                                 |
| flex_min                   | Float                 | Flexibilidade mínima.                                 |
| seasonality_max            | Float                 | Limite superior para sazonalidade.                    |
| seasonality_min            | Float                 | Limite inferior para sazonalidade.                    |
| fee_tax                    | Float                 | Valor de fee.                                         |
| energy_note_date           | String?               | Data da nota fiscal de energia (opcional).            |
| has_proinfa_discount       | Boolean               | Indica se há desconto PROINFA.                        |
| is_active                  | Boolean               | Indica se o contrato está ativo.                      |
| automatic_billing_released | Boolean               | Liberação para faturamento automático.                |
| created_at                 | DateTime              | Data de criação.                                      |
| updated_at                 | DateTime              | Data de atualização.                                  |
| looses                     | Float                 | Percentual de perdas (padrão: 0.03).                  |
| trader_id                  | String?               | Identificador de comercializadora vinculada.          |

## 🔗 Relacionamentos

- **Trader (N:1)**  
  Cada contrato pertence a **uma comercializadora**.
- **ContractSeasonality (1:N)**  
  Contém sazonalidades por ano.

---

# 🟩 2. Tabela `contracts_seasonalities` (model ContractSeasonality)

Armazena a **curva sazonal anual** de cada contrato, incluindo volumes mensais e preço.

## 🔑 Chave Primária

- **id** (String, uuid)

## 📝 Descrição das Colunas

| Coluna              | Tipo     | Descrição                        |
| ------------------- | -------- | -------------------------------- |
| year                | Int      | Ano da sazonalidade (ex: 2025).  |
| price_energy        | Float    | Preço da energia no ano.         |
| medium_volume       | Float    | Volume médio contratado.         |
| financial_guarantee | Boolean  | Se há garantia financeira ativa. |
| january — december  | Float    | Volume de energia por mês.       |
| created_at          | DateTime | Data de criação.                 |
| updated_at          | DateTime | Data de atualização.             |
| contract_id         | String?  | ID do contrato vinculado.        |

## 🔗 Relacionamento

- **Contract (N:1)**  
  Uma sazonalidade pertence a **um único contrato**.

---

# 🟧 3. Tabela `traders` (model Trader)

Tabela que representa as **comercializadoras** que atuam no sistema.

## 🔑 Chave Primária

- **id** (String, uuid)

## 📝 Descrição das Colunas

| Coluna    | Tipo     | Descrição                 |
| --------- | -------- | ------------------------- |
| name      | String   | Nome da comercializadora. |
| createdAt | DateTime | Data de criação.          |
| updatedAt | DateTime | Data de atualização.      |

## 🔗 Relacionamentos

- **contracts (1:N)**  
  Um Trader pode ter diversos contratos.
- **tradersProfiles (1:N)**  
  Perfis vinculados ao Trader.
- **responsibles (1:N)**  
  Contatos responsáveis pelo Trader.

---

# 🔵 Resumo Geral dos Relacionamentos

| Tabela              | Relacionamento      | Tipo | Descrição                                       |
| ------------------- | ------------------- | ---- | ----------------------------------------------- |
| Contract            | Trader              | N:1  | Um contrato pertence a uma comercializadora.    |
| Contract            | ContractSeasonality | 1:N  | Um contrato possui várias sazonalidades.        |
| ContractSeasonality | Contract            | N:1  | Sazonalidade vinculada a um contrato.           |
| Trader              | Contract            | 1:N  | Uma comercializadora gerencia vários contratos. |

---

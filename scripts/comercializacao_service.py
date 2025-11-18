from __future__ import annotations

from typing import Any, Dict, List, Tuple
from datetime import date, datetime

from scripts.database import read_records, read_records_in


DEBUG_PREFIX = "[ComercializacaoService]"


def _debug_print(message: str, *, data: Any | None = None) -> None:
    print(f"{DEBUG_PREFIX} {message}")
    if data is not None:
        print(f"{DEBUG_PREFIX} -> {data}")


MONTH_KEYS: List[str] = [
    "january",
    "february",
    "march",
    "april",
    "may",
    "june",
    "july",
    "august",
    "september",
    "october",
    "november",
    "december",
]

MONTH_LABELS: List[str] = [
    "Jan",
    "Fev",
    "Mar",
    "Abr",
    "Mai",
    "Jun",
    "Jul",
    "Ago",
    "Set",
    "Out",
    "Nov",
    "Dez",
]


def list_contract_clients() -> List[str]:
    """Retorna a lista de clientes distintos.

    Considera:
    - compradores a partir de `contracts.contractor`;
    - vendedores a partir de `traders.name`.
    """
    contracts = read_records("contracts", filters=None)
    traders = read_records("traders", filters=None)

    contractor_names = {
        str(record.get("contractor"))
        for record in contracts
        if record.get("contractor")
    }

    trader_names = {
        str(trader.get("name"))
        for trader in traders
        if trader.get("name")
    }

    clients = contractor_names | trader_names

    return sorted(clients)


def _parse_year_from_date(value: Any) -> int | None:
    if value is None:
        return None
    if isinstance(value, (datetime, date)):
        return value.year
    s = str(value)
    if not s:
        return None
    try:
        return datetime.fromisoformat(s).year
    except Exception:
        try:
            return int(s[:4])
        except Exception:
            return None


def get_client_dashboard_data(client_name: str) -> Dict[str, Any]:
    """Calcula métricas e séries de volumes por ano para um cliente.

    Compra:
      - contratos onde `contractor == client_name`.

    Venda:
      - contratos onde o `trader_id` está associado a um Trader com
        `name == client_name`.
    """
    # Contratos em que o cliente é comprador
    buy_contracts = read_records("contracts", filters={"contractor": client_name})
    _debug_print(
        f"Cliente {client_name}: contratos de COMPRA encontrados",
        data=[
            {
                "id": contract.get("id"),
                "contract_start_date": contract.get("contract_start_date"),
                "contract_end_date": contract.get("contract_end_date"),
            }
            for contract in buy_contracts
        ],
    )

    # Traders cujo nome corresponde ao cliente
    traders = read_records("traders", filters={"name": client_name})
    trader_ids: List[str] = [
        str(t["id"]) for t in traders if t.get("id") is not None
    ]

    # Contratos em que o cliente é vendedor
    sell_contracts: List[Dict[str, Any]] = []
    if trader_ids:
        sell_contracts = read_records_in("contracts", "trader_id", trader_ids)
    _debug_print(
        f"Cliente {client_name}: contratos de VENDA encontrados",
        data=[
            {
                "id": contract.get("id"),
                "contract_start_date": contract.get("contract_start_date"),
                "contract_end_date": contract.get("contract_end_date"),
            }
            for contract in sell_contracts
        ],
    )

    contracts_by_id: Dict[str, Dict[str, Any]] = {}
    directions_by_id: Dict[str, str] = {}
    contract_year_ranges: Dict[str, Tuple[int | None, int | None]] = {}

    for contract in buy_contracts:
        cid_raw = contract.get("id")
        if cid_raw is None:
            continue
        cid = str(cid_raw)
        contracts_by_id[cid] = contract
        directions_by_id[cid] = "buy"

    for contract in sell_contracts:
        cid_raw = contract.get("id")
        if cid_raw is None:
            continue
        cid = str(cid_raw)
        contracts_by_id[cid] = contract
        directions_by_id[cid] = "sell"

    allowed_years: set[int] = set()

    for cid, contract in contracts_by_id.items():
        start_year = _parse_year_from_date(contract.get("contract_start_date"))
        end_year = _parse_year_from_date(contract.get("contract_end_date"))
        if start_year is not None and end_year is not None and end_year < start_year:
            start_year, end_year = end_year, start_year
        contract_year_ranges[cid] = (start_year, end_year)

        if start_year is not None and end_year is not None:
            for year in range(start_year, end_year + 1):
                allowed_years.add(year)
        elif start_year is not None:
            allowed_years.add(start_year)
        elif end_year is not None:
            allowed_years.add(end_year)

    _debug_print(
        "Intervalos de anos por contrato",
        data=[
            {
                "contract_id": cid,
                "direction": directions_by_id.get(cid),
                "start_year": start_year,
                "end_year": end_year,
            }
            for cid, (start_year, end_year) in contract_year_ranges.items()
        ],
    )

    all_contracts: List[Dict[str, Any]] = list(contracts_by_id.values())

    total_contracts = len(all_contracts)
    active_contracts = sum(1 for c in all_contracts if bool(c.get("is_active")))
    inactive_contracts = total_contracts - active_contracts

    contract_ids: List[str] = list(contracts_by_id.keys())

    if not contract_ids:
        return {
            "total_contracts": total_contracts,
            "active_contracts": active_contracts,
            "inactive_contracts": inactive_contracts,
            "years": {},
        }

    # Busca todas as sazonalidades e filtra em memória para evitar
    # problemas com tipos/nomes de colunas no filtro remoto.
    all_seasonalities: List[Dict[str, Any]] = read_records(
        "contracts_seasonalities",
        filters=None,
    )
    _debug_print(
        "Total de linhas em contracts_seasonalities",
        data=len(all_seasonalities),
    )

    contract_ids_set = set(contract_ids)
    seasonalities: List[Dict[str, Any]] = []
    for row in all_seasonalities:
        raw_contract_id = row.get("contract_id")
        if raw_contract_id is None:
            raw_contract_id = row.get("contractId")
        if raw_contract_id is None:
            continue
        cid = str(raw_contract_id)
        if cid not in contract_ids_set:
            continue
        seasonalities.append(row)

    _debug_print(
        "Sazonalidades vinculadas ao cliente",
        data=[
            {
                "contract_id": row.get("contract_id") or row.get("contractId"),
                "year": row.get("year"),
            }
            for row in seasonalities
        ],
    )

    years: Dict[int, Dict[str, Any]] = {}

    for row in seasonalities:
        raw_contract_id = row.get("contract_id")
        if raw_contract_id is None:
            raw_contract_id = row.get("contractId")
        if raw_contract_id is None:
            continue

        cid = str(raw_contract_id)
        direction = directions_by_id.get(cid)
        if direction is None:
            continue

        year_value = row.get("year")
        if year_value is None:
            continue
        try:
            year = int(year_value)
        except (TypeError, ValueError):
            continue
        if year <= 0:
            continue

        year_data = years.setdefault(
            year,
            {
                "months": MONTH_LABELS,
                "buy": [0.0] * 12,
                "sell": [0.0] * 12,
            },
        )

        for index, month_key in enumerate(MONTH_KEYS):
            value = float(row.get(month_key) or 0.0)
            if direction == "buy":
                year_data["buy"][index] += value
            else:
                year_data["sell"][index] += value

    if allowed_years:
        for year in list(years.keys()):
            if year not in allowed_years:
                _debug_print(
                    "Removendo ano fora do intervalo dos contratos",
                    data={"year": year, "allowed_years": sorted(allowed_years)},
                )
                years.pop(year)
        for year in sorted(allowed_years):
            years.setdefault(
                year,
                {
                    "months": MONTH_LABELS,
                    "buy": [0.0] * 12,
                    "sell": [0.0] * 12,
                },
            )

    _debug_print(
        "Anos permitidos considerando contratos",
        data=sorted(allowed_years) if allowed_years else "(todos)",
    )

    _debug_print(
        "Resumo final de anos agregados",
        data={
            year: {
                "buy_total": sum(data["buy"]),
                "sell_total": sum(data["sell"]),
            }
            for year, data in years.items()
        },
    )

    return {
        "total_contracts": total_contracts,
        "active_contracts": active_contracts,
        "inactive_contracts": inactive_contracts,
        "years": years,
    }

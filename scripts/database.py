"""Módulo de conexão com bancos de dados Supabase.

Este módulo centraliza a configuração dos clientes Supabase principal e
auxiliar (somente leitura), além de expor funções de CRUD simples.
"""

from __future__ import annotations

import os
from typing import Any, Dict, List, Optional

from dotenv import load_dotenv
from supabase import Client, create_client

# Carrega variáveis de ambiente a partir de um arquivo .env, se existir
load_dotenv()


class DatabaseError(Exception):
    """Erro genérico para operações de banco de dados."""


def _create_supabase_client(url: Optional[str], key: Optional[str]) -> Optional[Client]:
    """Cria um cliente Supabase de forma segura.

    Retorna None caso URL ou KEY não estejam configurados.
    """
    if not url or not key:
        return None

    try:
        return create_client(url, key)
    except Exception as exc:  # pragma: no cover - log simples
        # Em um projeto real, considere usar logging estruturado
        print(f"Erro ao criar cliente Supabase: {exc}")
        return None


SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY") or os.getenv("SUPABASE_ANON_KEY")
SUPABASE_AUX_URL = os.getenv("SUPABASE_AUX_URL")
SUPABASE_AUX_KEY = os.getenv("SUPABASE_AUX_KEY")

_primary_client: Optional[Client] = _create_supabase_client(SUPABASE_URL, SUPABASE_KEY)
_aux_client: Optional[Client] = _create_supabase_client(SUPABASE_AUX_URL, SUPABASE_AUX_KEY)


def _ensure_primary() -> Client:
    if _primary_client is None:
        raise DatabaseError(
            "Cliente Supabase principal não configurado. "
            "Verifique as variáveis SUPABASE_URL e SUPABASE_KEY."
        )
    return _primary_client


def _ensure_aux() -> Client:
    if _aux_client is None:
        raise DatabaseError(
            "Cliente Supabase auxiliar não configurado. "
            "Verifique as variáveis SUPABASE_AUX_URL e SUPABASE_AUX_KEY."
        )
    return _aux_client


def create_record(table: str, data: Dict[str, Any]) -> Dict[str, Any]:
    """Cria um registro em uma tabela usando o banco principal."""
    client = _ensure_primary()
    try:
        response = client.table(table).insert(data).execute()
        if getattr(response, "error", None):
            raise DatabaseError(str(response.error))
        return getattr(response, "data", {}) or {}
    except Exception as exc:  # pragma: no cover
        raise DatabaseError(f"Erro ao criar registro em {table}: {exc}")


def read_records(
    table: str,
    filters: Optional[Dict[str, Any]] = None,
    *,
    use_aux: bool = False,
) -> List[Dict[str, Any]]:
    """Lê registros de uma tabela.

    Quando `use_aux=True`, utiliza o banco auxiliar (somente leitura).
    """
    client = _ensure_aux() if use_aux else _ensure_primary()

    try:
        query = client.table(table).select("*")
        filters = filters or {}
        for key, value in filters.items():
            query = query.eq(key, value)
        response = query.execute()
        if getattr(response, "error", None):
            raise DatabaseError(str(response.error))
        return getattr(response, "data", []) or []
    except Exception as exc:  # pragma: no cover
        raise DatabaseError(f"Erro ao ler registros em {table}: {exc}") from exc


def read_records_in(
    table: str,
    column: str,
    values: List[Any],
    *,
    use_aux: bool = False,
) -> List[Dict[str, Any]]:
    """Lê registros utilizando filtro IN em uma coluna."""
    if not values:
        return []

    client = _ensure_aux() if use_aux else _ensure_primary()

    try:
        query = client.table(table).select("*").in_(column, values)
        response = query.execute()
        if getattr(response, "error", None):
            raise DatabaseError(str(response.error))
        return getattr(response, "data", []) or []
    except Exception as exc:  # pragma: no cover
        raise DatabaseError(f"Erro ao ler registros em {table} com filtro IN: {exc}") from exc


def update_record(table: str, record_id: Any, data: Dict[str, Any]) -> Dict[str, Any]:
    """Atualiza um registro em uma tabela usando o banco principal."""
    client = _ensure_primary()
    try:
        response = (
            client.table(table)
            .update(data)
            .eq("id", record_id)
            .execute()
        )
        if getattr(response, "error", None):
            raise DatabaseError(str(response.error))
        result = getattr(response, "data", []) or []
        return result[0] if result else {}
    except Exception as exc:  # pragma: no cover
        raise DatabaseError(f"Erro ao atualizar registro em {table}: {exc}") from exc


def delete_record(table: str, record_id: Any) -> None:
    """Remove um registro de uma tabela usando o banco principal."""
    client = _ensure_primary()
    try:
        response = client.table(table).delete().eq("id", record_id).execute()
        if getattr(response, "error", None):
            raise DatabaseError(str(response.error))
    except Exception as exc:  # pragma: no cover
        raise DatabaseError(f"Erro ao excluir registro em {table}: {exc}") from exc


def delete_records(table: str, filters: Dict[str, Any]) -> None:
    """Remove registros de uma tabela com base em filtros."""
    client = _ensure_primary()
    try:
        query = client.table(table).delete()
        for key, value in filters.items():
            query = query.eq(key, value)
        response = query.execute()
        if getattr(response, "error", None):
            raise DatabaseError(str(response.error))
    except Exception as exc:  # pragma: no cover
        raise DatabaseError(f"Erro ao excluir registros em {table}: {exc}") from exc

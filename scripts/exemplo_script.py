"""Script de exemplo para demonstrar separação entre lógica de negócios
 e camada de apresentação.
"""

from __future__ import annotations

from typing import Any, Dict


def processar_exemplo(mensagem: str) -> str:
    """Processa uma mensagem para exibição na tela de exemplo.

    Em um caso real, aqui poderia haver chamadas a banco de dados,
    validações de negócio ou integração com serviços externos.
    """
    mensagem_limpa = mensagem.strip() or "(mensagem vazia)"
    return f"Mensagem processada pelo script: {mensagem_limpa}"

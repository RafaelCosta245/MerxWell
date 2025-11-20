def calculate_icms_price(base_price: float, percentage: float) -> float:
    """
    Calcula o preço final sem ICMS dado um percentual de ICMS.
    """
    valor_inicial_com_icms = base_price / 0.795
    icms = valor_inicial_com_icms * 0.205
    desc_icms = percentage * icms
    valor_final_com_icms = valor_inicial_com_icms - desc_icms
    valor_final_sem_icms = valor_final_com_icms * 0.795
    return valor_final_sem_icms

def calculate_icms_price_star(base_price: float, percentage: float) -> float:
    """
    Calcula o preço final com desconto de ICMS (Lógica *).
    1. valor_inicial_com_icms = valor_base_encontrado / 0.795
    2. icms = valor_inicial_com_icms * 0.205
    3. desc_icms = percentual_icms * icms
    4. valor_final_sem_icms = valor_base_encontrado - desc_icms
    """
    valor_inicial_com_icms = base_price / 0.795
    icms = valor_inicial_com_icms * 0.205
    desc_icms = percentage * icms
    valor_final_sem_icms = base_price - desc_icms
    return valor_final_sem_icms

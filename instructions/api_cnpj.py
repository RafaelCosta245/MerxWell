import requests

CNPJ = "35998612000108"

def consultar_cnpj(cnpj: str, api_key: str):
    url = f"https://api.cnpja.com.br/companies/{cnpj}"
    headers = {
        "Authorization": api_key,
        "Accept": "application/json"
    }
    try:
        r = requests.get(url, headers=headers, timeout=10)
        r.raise_for_status()
        dados = r.json()
        print("=== Dados do CNPJ ===")
        print("Razão Social:", dados.get("razao_social") or dados.get("name"))
        print("Nome Fantasia:", dados.get("nome_fantasia") or dados.get("alias"))
        endereco = dados.get("address") or dados.get("endereco") or {}
        print("Endereço:")
        print("  Logradouro:", endereco.get("street") or endereco.get("logradouro"))
        print("  Número:", endereco.get("number") or endereco.get("numero"))
        print("  Bairro:", endereco.get("neighborhood") or endereco.get("bairro"))
        print("  Cidade:", endereco.get("city") or endereco.get("municipio"))
        print("  UF:", endereco.get("state") or endereco.get("estado"))
    except requests.exceptions.RequestException as e:
        print("Erro na requisição:", e)
    except ValueError:
        print("Erro ao decodificar JSON:", r.text)

if __name__ == "__main__":
    chave = "4e364762-1c62-4db1-b2e9-d1f7bbee33c4-64a76f78-b79f-43a7-acc2-0a2d2825e2df"  # substitua pela chave que você obteve
    consultar_cnpj(CNPJ, chave)

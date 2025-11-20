import requests
import certifi

url = "https://api.opencnpj.org/v1/empresa/19131243000197"

print("Usando CA bundle:", certifi.where())

try:
    r = requests.get(url, verify=certifi.where())
    print("Status:", r.status_code)
    print(r.text[:400])
except Exception as e:
    print("Erro:", type(e).__name__, e)

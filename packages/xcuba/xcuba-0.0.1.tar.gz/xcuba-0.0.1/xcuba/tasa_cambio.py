# mi_paquete/cambio.py

import requests
import json
from bs4 import BeautifulSoup

def obtener_tasas_eltoque() -> dict:
    url = 'https://eltoque.com/'
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0 Safari/537.3'
    }

    response = requests.get(url, headers=headers)
    if response.status_code != 200:
        raise Exception("No se pudo acceder a eltoque.com")

    soup = BeautifulSoup(response.text, features='html.parser')
    rows = soup.find_all('tr')

    exchange_rates = {}
    for row in rows:
        try:
            currency_cell = row.find('td', class_='name-cell')
            price_cell = row.find('td', class_='price-cell')
            if currency_cell and price_cell:
                currency_span = currency_cell.find('span', class_='currency')
                if currency_span:
                    currency_text = currency_span.get_text(strip=True).replace('<!-- -->', '').strip()
                    parts = currency_text.split()
                    currency = parts[0].replace('1', '').strip()

                    price_span = price_cell.find('span', class_='price-text')
                    if price_span:
                        price_text = price_span.get_text(strip=True).replace('<!-- -->', '').strip()
                        price_parts = price_text.split()
                        price = price_parts[0].replace('CUP', '').strip()

                        exchange_rates[currency] = price
        except:
            continue  # Saltar errores silenciosamente

    return exchange_rates

def tasas_json() -> str:
    """Devuelve los datos como cadena JSON con indentación."""
    return json.dumps(obtener_tasas_eltoque(), indent=2, ensure_ascii=False)

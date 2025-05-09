import os
import json
import requests
from bs4 import BeautifulSoup
from datetime import datetime
import time

# Configuración
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36'
}
scimago_url = 'https://www.scimagojr.com'
search_url = 'https://www.scimagojr.com/journalsearch.php?q='
output_file = os.path.join('datos', 'json', 'scimago_data.json')
DELAY = 2

def scrap(url):
    try:
        response = requests.get(url, headers=headers, timeout=15)
        response.raise_for_status()
        return response
    except Exception as e:
        print(f"Error al obtener {url}: {str(e)}")
        return None

def find_journal_url(journal_title: str):
    try:
        journal_search_url = f"{search_url}{journal_title.replace(' ', '+')}"
        journal_search_page = scrap(journal_search_url)
        if not journal_search_page:
            return None
        soup = BeautifulSoup(journal_search_page.text, 'html.parser')
        first_result = soup.select_one('span.jrnlname')
        if not first_result:
            return None
        journal_url = first_result.find_parent('a')['href']
        return f'{scimago_url}/{journal_url}'
    except Exception as e:
        print(f"Error buscando {journal_title}: {str(e)}")
        return None

def get_h_index(journal_url: str) -> str:
    try:
        journal_site = scrap(journal_url)
        if not journal_site:
            return 'N/A'
        soup = BeautifulSoup(journal_site.text, 'html.parser')
        h2 = soup.find('h2', string='H-Index')
        if h2:
            return h2.find_next_sibling('p').text.strip()
        h_index_section = soup.find('a', {'name': 'h-index'})
        if h_index_section:
            return h_index_section.find_next('div').text.strip()
        return 'N/A'
    except Exception as e:
        print(f"Error obteniendo H-Index de {journal_url}: {str(e)}")
        return 'N/A'
    
def get_homepage(journal_url: str) -> str:
    try:
        journal_site = scrap(journal_url)
        if not journal_site:
            return 'N/A'
        soup = BeautifulSoup(journal_site.text, 'html.parser')
        homepage_link = soup.find('a', string='Homepage')
        if homepage_link and homepage_link.has_attr('href'):
            return homepage_link['href'].strip()
        return 'N/A'
    except Exception as e:
        print(f"Error obteniendo homepage de {journal_url}: {str(e)}")
        return 'N/A'

def get_publisher(journal_url: str) -> str:
    try:
        journal_site = scrap(journal_url)
        if not journal_site:
            return 'N/A'
        soup = BeautifulSoup(journal_site.text, 'html.parser')
        
        # Buscar el encabezado Publisher
        publisher_header = soup.find('h2', string='Publisher')
        if publisher_header:
            # Buscar el siguiente <a> después del <h2>
            publisher_link = publisher_header.find_next('a')
            if publisher_link and publisher_link.text:
                return publisher_link.text.strip()
        return 'N/A'
    except Exception as e:
        print(f"Error obteniendo publisher de {journal_url}: {str(e)}")
        return 'N/A'


def get_journal_data(journal_url: str):
    try:
        return {
            'url': journal_url,
            'h_index': get_h_index(journal_url),
            'get_homepage': get_homepage(journal_url),
            'get_publisher': get_publisher(journal_url),
            'last_update': datetime.now().isoformat()
        }
    except Exception as e:
        print(f"Error extrayendo datos de {journal_url}: {str(e)}")
        return None

def main():
    journal_name = 'World Psychiatry'

    journal_url = find_journal_url(journal_name)
    if journal_url:
        time.sleep(DELAY)
        journal_data = get_journal_data(journal_url)
        if journal_data:
            print("Datos obtenidos con éxito:")
            print(json.dumps(journal_data, indent=2))
        else:
            print("No se pudieron obtener los datos")
    else:
        print(f"No se encontró la revista {journal_name}")

if __name__ == '__main__':
    main()

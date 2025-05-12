from flask import Flask, render_template, request
import json
from urllib.parse import unquote
from collections import defaultdict
import os

app = Flask(__name__)

# Cargar datos de revistas
with open(os.path.join("datos", "json", "journals.json"), 'r', encoding='utf-8') as f:
    JOURNALS_DATA = json.load(f)

def normalize_text(text):
    """Normaliza texto para búsquedas insensibles a mayúsculas/acentos"""
    return unquote(str(text)).lower().strip()

# Obtener las áreas de los CSV
def get_areas()->list:
    areas = []
    areas_files = os.listdir(os.path.join("datos", "csv", "areas"))
    for file in areas_files:
        areas.append(file.removesuffix(" RadGridExport.csv"))
    return areas

# Obtener los catálogos de los CSV
def get_catalogs()->list:
    catalogs = []
    catalogs_files = os.listdir(os.path.join("datos", "csv", "catalogos"))
    for file in catalogs_files:
        catalogs.append(file.removesuffix("_RadGridExport.csv"))
    return catalogs

# Obtener revistas en cierta área
def journals_in_area(area_name)->list:
    journals_in_area = []
    for journal in JOURNALS_DATA:
        journal_areas = journal.get('areas')
        if not isinstance(journal_areas, list):
            continue
        
        if area_name in journal_areas:
            journals_in_area.append(journal)    
    return journals_in_area

# Obtener revistas en cierto catálogo
def journals_in_catalog(catalog_name)->list:
    journals_in_catalog = []
    for journal in JOURNALS_DATA:
        journal_catalogs = journal.get('catalogs')
        if not isinstance(journal_catalogs, list):
            continue
        
        if catalog_name in journal_catalogs:
            journals_in_catalog.append(journal)    
    return journals_in_catalog

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/search')
def search():
    query = normalize_text(request.args.get('q', ''))
    results = []
    
    if query:
        search_terms = query.split()
        
        for journal in JOURNALS_DATA:
            # Campos donde buscar
            search_fields = [
                journal.get('title', ''),
                journal.get('publisher', ''),
                ' '.join(journal.get('categories', {}).keys()) if isinstance(journal.get('categories'), dict) else ''
            ]
            
            # Buscar en todos los campos
            match = any(
                any(term in normalize_text(field) for field in search_fields if field)
                for term in search_terms
            )
            
            if match:
                results.append(journal)
    
    return render_template('search.html', results=results, query=query)

@app.route('/journal/<path:journal_title>')
def journal_detail(journal_title):
    journal = next((j for j in JOURNALS_DATA 
                  if normalize_text(j['title']) == normalize_text(journal_title)), None)
    if not journal:
        return "Revista no encontrada", 404
    
    return render_template('journal_detail.html', journal=journal)

# RUTA PARA EXPLORA (con abecedario)
@app.route('/explora')
def explora():
    return render_template('explora.html', letra_actual=None)

# RUTA PARA EXPLORAR REVISTAS POR LETRA
@app.route('/explorar/<letra>')
def explorar_por_letra(letra):
    letra = letra.upper()
    revistas_filtradas = [
        journal for journal in JOURNALS_DATA
        if journal.get('title', '').upper().startswith(letra)
    ]
    return render_template('explora.html', letra_actual=letra, resultados=revistas_filtradas)

@app.route("/areas")
def areas():
    areas_list = get_areas()
    return render_template('areas.html', areas=areas_list)

@app.route("/area")
def area():
    area_name = normalize_text(request.args.get('a', ''))
    area_str = area_name.upper()
    query = normalize_text(request.args.get('q', ''))
    journals_area = journals_in_area(area_str)

    if query:
        search_terms = query.split()
        filtered = []
        for journal in journals_area:
            # Campos donde buscar
            search_fields = [
                journal.get('title', ''),
                journal.get('publisher', ''),
                ' '.join(journal.get('categories', {}).keys()) if isinstance(journal.get('categories'), dict) else ''
            ]
            
            # Buscar en todos los campos
            match = any(
                any(term in normalize_text(field) for field in search_fields if field)
                for term in search_terms
            )
            
            if match:
                filtered.append(journal)
        journals_area = filtered

    return render_template('area.html', area=area_str, journals=journals_area, query=query)

@app.route("/catalogs")
def catalogos():
    catalogs_list = get_catalogs()
    return render_template('catalogs.html', catalogs=catalogs_list)

@app.route("/catalog")
def catalog():
    catalog_name = normalize_text(request.args.get('c', ''))
    catalog_str = catalog_name.upper()
    query = normalize_text(request.args.get('q', ''))
    journals_catalog = journals_in_catalog(catalog_str)

    if query:
        search_terms = query.split()
        filtered_c = []
        for journal in journals_catalog:
            # Campos donde buscar
            search_fields = [
                journal.get('title', ''),
                journal.get('publisher', ''),
                ' '.join(journal.get('categories', {}).keys()) if isinstance(journal.get('categories'), dict) else ''
            ]
            
            # Buscar en todos los campos
            match = any(
                any(term in normalize_text(field) for field in search_fields if field)
                for term in search_terms
            )
            
            if match:
                filtered_c.append(journal)
        journals_catalog = filtered_c

    return render_template('catalog.html', catalog=catalog_str, journals=journals_catalog, query=query)

@app.route('/credits')
def credits():
    return render_template('credits.html')

if __name__ == '__main__':
    app.run(debug=True)

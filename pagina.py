from flask import Flask, render_template, request
import json
from urllib.parse import unquote
from collections import defaultdict

app = Flask(__name__)

# Cargar datos de revistas
with open('segundo_otman.json', 'r', encoding='utf-8') as f:
    JOURNALS_DATA = json.load(f)

def normalize_text(text):
    """Normaliza texto para búsquedas insensibles a mayúsculas/acentos"""
    return unquote(str(text)).lower().strip()

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


@app.route('/credits')
def credits():
    return render_template('credits.html')

if __name__ == '__main__':
    app.run(debug=True)

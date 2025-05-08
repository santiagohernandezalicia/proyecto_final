import os
import csv
import json

''' Lector de archivo CSV y creador de diccionario de revistas '''

def detectar_encoding(archivo)->str:
    """Intenta detectar la codificación del archivo"""
    encodings = ['utf-8', 'iso-8859-1', 'windows-1252']
    for enc in encodings:
        try:
            with open(f"datos/csv/areas/{archivo}", 'r', encoding=enc) as f:
                f.read(10000)  # Leer una parte del archivo
                return enc
        except UnicodeDecodeError:
            continue
    return 'iso-8859-1'  # Por defecto si no se detecta

def main():
    ''' Función principal '''
    diccionario_revistas = {}
    archivos_areas = os.listdir("datos/csv/areas")
    for archivo in archivos_areas:
        enc = detectar_encoding(archivo)
        with open(f"datos/csv/areas/{archivo}", "r", encoding=enc) as f:
            reader = csv.DictReader(f)
            area = archivo.removesuffix(" RadGridExport.csv")
            for row in reader:
                titulo = row['TITULO:']
                if titulo in diccionario_revistas:
                    diccionario_revistas[titulo]['areas'].append(area)
                else:
                    diccionario_revistas[titulo] = {"areas":[area], "catalogos":[]}
    archivos_catalogos = os.listdir("datos/csv/catalogos")
    for archivo in archivos_catalogos:
        with open(f"datos/csv/catalogos/{archivo}", "r", encoding=enc) as f:
            reader = csv.DictReader(f)
            catalogo = archivo.removesuffix("_RadGridExport.csv")
            for row in reader:
                titulo = row['TITULO:']
                if titulo in diccionario_revistas:
                    diccionario_revistas[titulo]['catalogos'].append(catalogo)
    print(diccionario_revistas['2D MATERIALS'])
    with open('datos/json/prueba.json', 'w', encoding='latin-1') as archivo_json:
        json.dump(diccionario_revistas, archivo_json)

if __name__ == "__main__":
    ''' Llamar a la función principal '''
    main()
from enum import unique
from flask import Flask, jsonify, render_template, request
import sqlite3
import json
import requests
import json

app = Flask(__name__)

class Taxonomy:
    def __init__(self, kingdom, phylum, _class,order, family, genus, species):
        self.kingdom = kingdom
        self.phylum = phylum
        self._class = _class
        self.order = order
        self.family = family
        self.genus = genus
        self.subgenus = species

class SpeciesData:
    def __init__(self, usage_key, synonyms, vernecular, distribuition, descrition):
        self.key = usage_key
        self.synonyms = synonyms
        self.vernecular = vernecular
        self.distribuition = distribuition
        self.descrition = descrition
        
class TrabalharComJson:
    def __init__(self, data, type='standard'):
        self.data = data
        self.type = type

    def save_json(self, filename):
        with open(filename, 'w', encoding='utf-8') as file:
            if self.type == 'standard':
                json.dump(self.data, file, ensure_ascii=False, indent=4)
            elif self.type == 'compacto':
                json.dump(self.data, file, ensure_ascii=False)
            # Adicione mais condições conforme necessário
    
    def load_json(self, filename):
        with open(filename, 'r', encoding='utf-8') as file:
            if self.type == 'standard':
                return json.load(file)
            elif self.type == 'compacto':
                # Supondo que você queira tratar de forma diferente ao carregar
                data = json.load(file)
                # Modifique data conforme necessário para o tipo compacto
                return data
            # Adicione mais condições conforme necessário
    

def default_converter(o):
    if hasattr(o, '__dict__'):
        return o.__dict__
    elif isinstance(o, bytes):
        return o.decode('utf-8')  # Decodifica bytes para string usando UTF-8
    else:
        raise TypeError(f'Object of type {o.__class__.__name__} is not JSON serializable')
    

DATABASE = 'C:/Users/Carlinhos/Ibama/API/animals.db'

def get_db_connection():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn

@app.route('/kingdoms', methods=['GET'])
def get_kingdom_names():
    try:
        conn = get_db_connection()
        kingdoms = conn.execute('SELECT DISTINCT kingdom FROM animals').fetchall()
        conn.close()
        kingdoms_names = [k['kingdom'] for k in kingdoms if k['kingdom'] != ""]
        kingdoms_names.sort()
        return jsonify(kingdoms_names)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/phylums', methods=['GET'])
def get_phylums():
    selected_kingdom = request.args.get('kingdom', None)
    try:
        conn = get_db_connection()
        phylums = conn.execute('SELECT DISTINCT phylum FROM animals WHERE kingdom = ?', (selected_kingdom,)).fetchall()
        conn.close()
        phylums_names = [p['phylum'] for p in phylums if p['phylum'] != ""]
        phylums_names.sort()
        return jsonify(phylums_names)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/classes', methods=['GET'])
def get_classes():
    selected_class = request.args.get('phylum', None)
    try:
        conn = get_db_connection()
        classes = conn.execute('SELECT DISTINCT class FROM animals WHERE phylum = ?', (selected_class,)).fetchall()
        conn.close()
        class_names = [c['class'] for c in classes if c['class'] != ""]
        class_names.sort()
        return jsonify(class_names)
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    
@app.route('/orders', methods=['GET'])
def get_orders():
    selected_class = request.args.get('class', None)  # Mudança para capturar o parâmetro correto
    try:
        conn = get_db_connection()
        # Modifica a consulta para selecionar ordens baseadas na classe fornecida
        orders = conn.execute('SELECT DISTINCT "order" FROM animals WHERE class = ?', (selected_class,)).fetchall()
        conn.close()
        order_names = [o['order'] for o in orders if o['order'] != "" and o['order'] is not None]
        order_names.sort()  # Ordena os nomes das ordens
        return jsonify(order_names)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/families', methods=['GET'])
def get_families():
    selected_family = request.args.get('class', None)
    try:
        conn = get_db_connection()
        families = conn.execute('SELECT DISTINCT family FROM animals WHERE class = ?', (selected_family,)).fetchall()
        conn.close()
        families_names = [f['family'] for f in families if f['family'] != ""]
        families_names.sort()
        return jsonify(families_names)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/genus', methods=['GET'])
def get_genus():
    selected_genus = request.args.get('family', None)
    try:
        conn = get_db_connection()
        genus = conn.execute('SELECT DISTINCT genus FROM animals WHERE family = ?', (selected_genus,)).fetchall()
        conn.close()
        genus_names = [f['genus'] for f in genus if f['genus'] != ""]
        genus_names.sort()
        return jsonify(genus_names)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/subgenus', methods=['GET'])
def get_subgenus():
    selected_subgenus = request.args.get('genus', None)
    try:
        conn = get_db_connection()
        subgenus = conn.execute('SELECT DISTINCT specificEpithet FROM animals WHERE genus = ?', (selected_subgenus,)).fetchall()
        conn.close()
        subgenus_names = [f['specificEpithet'] for f in subgenus if f['specificEpithet'] not in (None,"")]
        return jsonify(subgenus_names)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/scientific_name', methods=['GET']) 
def get_scientific_name():
    selected_kingdom = request.args.get('kingdom', None)
    selected_phylum = request.args.get('phylum', None)
    selected_class = request.args.get('class', None)
    selected_orders = request.args.get('order', None)
    selected_family = request.args.get('family', None)
    selected_genus = request.args.get('genus', None)
    selected_subgenus = request.args.get('subgenus', None)
    
    specie_taxonomy = Taxonomy(selected_kingdom, selected_phylum, selected_class, selected_orders, selected_family, selected_genus, selected_subgenus)
    
    retorno = {}
    try:
        conn = get_db_connection()
        query = 'SELECT DISTINCT scientific_name FROM animals WHERE kingdom = ? AND phylum = ? AND class = ? AND "order" = ? AND family = ? AND genus = ? AND specificEpithet = ?'
        params = (specie_taxonomy.kingdom, specie_taxonomy.phylum, specie_taxonomy._class, specie_taxonomy.order, specie_taxonomy.family, specie_taxonomy.genus, specie_taxonomy.subgenus)
        #params = (selected_kingdom, selected_phylum, selected_class, selected_orders, selected_family, selected_genus, selected_subgenus,)
        result = conn.execute('SELECT DISTINCT scientific_name FROM animals WHERE kingdom = ? AND phylum = ? AND class = ? AND "order" = ? AND family = ? AND genus = ? AND specificEpithet = ?', params).fetchall()
        conn.close()
        if result:
            response_data_ = None
            scientific_names = [row['scientific_name'] for row in result]
            retorno["scientific_name"] = scientific_names[0]

            # Endpoint para buscar informações sobre uma espécie específica na API do GBIF
            species_url = f'https://api.gbif.org/v1/species/match?name={scientific_names[0].replace(" ", "%20")}'

            # Fazendo a requisição para o endpoint
            response = requests.get(species_url)
            if response.status_code == 200:
                species_data = response.json()
                
                # Obtendo o 'usageKey' que é necessário para buscar sinônimos
                usage_key = species_data.get('usageKey')
                
                # Se 'usageKey' foi encontrado, buscar sinônimos
                # Response_data[] é um array de dicionários com as informações da espécie encontrada na API do GBIF 
                
                if usage_key:
                    response_data = []
                    synonyms_url = f'https://api.gbif.org/v1/species/{usage_key}/synonyms'
                    synonyms_response = requests.get(synonyms_url)
                    vernecular_names_url = f'https://api.gbif.org/v1/species/{usage_key}/vernacularNames'
                    vernecular_names_response = requests.get(vernecular_names_url)
                    distribuition_url = f'https://api.gbif.org/v1/species/{usage_key}/distributions'
                    distribuition_response = requests.get(distribuition_url)
                    descrition_url = f'https://api.gbif.org/v1/species/{usage_key}/descriptions'
                    descrition_response = requests.get(descrition_url)
                    
                    if synonyms_response.status_code == 200:
                        synonyms_response_data = synonyms_response.json()
                        response_data.append(synonyms_response_data)
                    if vernecular_names_response.status_code == 200:
                        vernecular_names_response_data = vernecular_names_response.json()
                        response_data.append(vernecular_names_response_data)
                    if distribuition_response.status_code == 200:
                        distribuition_response_data = distribuition_response.json()
                        response_data.append(distribuition_response_data)
                    if descrition_response.status_code == 200:
                        descrition_response_data = descrition_response.json()
                        response_data.append(descrition_response_data)
                        
                    #retorno['species_data'] = response_data
                    response_data_ = SpeciesData(usage_key, response_data[0], response_data[1], response_data[2], response_data[3])
                else:
                    print("Espécie não encontrada ou 'usageKey' não disponível")
            else:
                print("Erro ao buscar informações da espécie")
            # Code block end

            return scientific_names[0], response_data_.key, response_data_.synonyms, response_data_.vernecular, response_data_.distribuition, response_data_.descrition
        else:
            return jsonify({"error": "No scientific name found for the given criteria"}), 404, 404, 404, 404, 404
    except Exception as e:
        return jsonify({"error": str(e)}), 500, 500, 500, 500, 500

@app.route('/', methods=['GET'])
def index():
    selected_kingdom = request.args.get('kingdom', None)
    selected_phylum = request.args.get('phylum', None)
    selected_class = request.args.get('class', None)
    selected_order = request.args.get('order', None)
    selected_family = request.args.get('family', None)
    selected_genus = request.args.get('genus', None)
    selected_subgenus = request.args.get('subgenus', None)

    kingdoms = get_kingdom_names().get_json()
    phyla = get_phylums().get_json() if selected_kingdom else []
    classes = get_classes().get_json() if selected_phylum else []
    orders = get_orders().get_json() if selected_class else []
    families = get_families().get_json() if selected_order else []
    genera = get_genus().get_json() if selected_family else []
    subgenera = get_subgenus().get_json() if selected_genus else []
    scientific_name_, usage_key_, synonyms_, vernecular_, distribuition_, descrition_ = get_scientific_name()
    
    return render_template('index.html', 
                           kingdoms=kingdoms, 
                           selected_kingdom=selected_kingdom, 
                           phyla=phyla, 
                           selected_phylum=selected_phylum, 
                           classes=classes, 
                           selected_class=selected_class,
                           orders=orders,
                           selected_order=selected_order,
                           families=families, 
                           selected_family=selected_family, 
                           genera=genera, 
                           selected_genus=selected_genus, 
                           subgenera=subgenera, 
                           selected_subgenus=selected_subgenus,
                           scientific_name=scientific_name_,
                           usage_key=usage_key_,
                           synonyms=synonyms_,
                           vernecular=vernecular_,
                           distribuition=distribuition_,
                           descrition=descrition_)

if __name__ == '__main__':
    app.run(debug=True)
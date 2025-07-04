# Configurações específicas da ontologia.
import os
import json
import glob # Importar glob para encontrar ficheiros
import rdflib # Importar rdflib para carregar ontologias

# Caminho para o diretório onde as ontologias são armazenadas
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
ONTOLOGIES_DIR = os.path.join(PROJECT_ROOT, "ontologies")

# Nome do ficheiro de configuração da ontologia ativa (pode ser definido em settings.py ou env var)
# Esta variável pode tornar-se menos relevante se ativarmos por nome de ficheiro .owl
ACTIVE_ONTOLOGY_CONFIG_FILE = os.getenv("ACTIVE_ONTOLOGY_CONFIG", "default_ontology_props.json")

DEFAULT_ONTOLOGY_SETTINGS = {
    "ontology_file": None, # Será preenchido com o nome do ficheiro .owl ou .ttl
    "ontology_format": None, # Será inferido ou definido (ex: "owl", "turtle", "xml")
    "RDF_BASE_URI": "http://example.org/ontology#", # Base URI genérica
    "ITEM_CLASS": "owl:Thing", # Classe mais genérica como fallback
    "TITLE_PROPERTY": "rdfs:label", # Propriedade comum como fallback
    "AUTHOR_PROPERTY": "dcterms:creator", # Propriedade comum como fallback
    "DESCRIPTION_PROPERTY": "dcterms:description", # Propriedade comum como fallback
    "PREFIXES": {
        "rdf": str(rdflib.RDF),
        "rdfs": str(rdflib.RDFS),
        "owl": str(rdflib.OWL),
        "dcterms": "http://purl.org/dc/terms/",
        "foaf": "http://xmlns.com/foaf/0.1/",
        "ex": "http://example.org/ontology#" # Prefixo de exemplo
    }
}

def find_available_ontology_files(extensions=["owl", "ttl", "rdf", "xml"]):
    """Encontra todos os ficheiros de ontologia suportados no diretório."""
    if not os.path.isdir(ONTOLOGIES_DIR):
        print(f"Aviso: Diretório de ontologias não encontrado em {ONTOLOGIES_DIR}")
        return []
    
    found_files = []
    for ext in extensions:
        pattern = os.path.join(ONTOLOGIES_DIR, f"*.{ext}")
        found_files.extend([os.path.basename(f) for f in glob.glob(pattern)])
    
    # Remover duplicados se um ficheiro tiver extensão dupla (improvável mas seguro)
    unique_files = sorted(list(set(found_files)))
    print(f"Ficheiros de ontologia encontrados em {ONTOLOGIES_DIR}: {unique_files}")
    return unique_files

def generate_config_from_owl(owl_filename):
    """Gera uma configuração básica a partir de um nome de ficheiro .owl."""
    filepath = os.path.join(ONTOLOGIES_DIR, owl_filename)
    if not os.path.exists(filepath):
        raise FileNotFoundError(f"Ficheiro de ontologia {owl_filename} não encontrado em {ONTOLOGIES_DIR}")

    # Começar com as configurações padrão
    config = DEFAULT_ONTOLOGY_SETTINGS.copy()
    config["ontology_file"] = owl_filename
    config["ontology_file_path"] = filepath
    # Tentar inferir o formato, mas rdflib geralmente faz isso bem
    config["ontology_format"] = rdflib.util.guess_format(filepath) or "xml" # Default para XML/RDF se não conseguir adivinhar
    
    # Tentar extrair a base URI da ontologia (se definida)
    try:
        g = rdflib.Graph()
        g.parse(filepath, format=config["ontology_format"])
        # Procurar por declarações de owl:Ontology para obter a URI base
        # Isto pode não funcionar para todas as ontologias
        for s, p, o in g.triples((None, rdflib.RDF.type, rdflib.OWL.Ontology)):
            if isinstance(s, rdflib.URIRef):
                config["RDF_BASE_URI"] = str(s) # Usa a URI da própria ontologia como base
                # Tentar definir um prefixo para a base URI
                config["PREFIXES"]["onto"] = str(s) # Adiciona um prefixo 'onto'
                break # Usa a primeira encontrada
    except Exception as e:
        print(f"Aviso: Não foi possível analisar {owl_filename} para extrair a base URI: {e}")

    print(f"Configuração gerada para {owl_filename}: {config}")
    return config

def load_ontology_config(config_or_owl_filename=ACTIVE_ONTOLOGY_CONFIG_FILE):
    """Carrega a configuração de um ficheiro JSON ou gera a partir de um ficheiro .owl."""
    if config_or_owl_filename.lower().endswith(".json"):
        # Carregar de ficheiro JSON (lógica anterior adaptada)
        config_path = os.path.join(ONTOLOGIES_DIR, config_or_owl_filename)
        try:
            with open(config_path, 'r') as f:
                config = json.load(f)
                print(f"Configuração da ontologia carregada de JSON: {config_path}")
                # Validar e completar com defaults
                for key, value in DEFAULT_ONTOLOGY_SETTINGS.items():
                    if key not in config:
                        config[key] = value
                if "ontology_file_path" not in config and config.get("ontology_file"):
                     config["ontology_file_path"] = os.path.join(ONTOLOGIES_DIR, config["ontology_file"])
                return config
        except FileNotFoundError:
            print(f"Aviso: Ficheiro de configuração JSON {config_or_owl_filename} não encontrado. A tentar gerar config default.")
            # Retornar defaults se o ficheiro especificado não for encontrado
            default_config_with_path = DEFAULT_ONTOLOGY_SETTINGS.copy()
            if default_config_with_path.get("ontology_file"):
                 default_config_with_path["ontology_file_path"] = os.path.join(ONTOLOGIES_DIR, default_config_with_path["ontology_file"])
            return default_config_with_path
        except json.JSONDecodeError:
            print(f"Erro: Ficheiro JSON {config_path} inválido. A usar config default.")
            default_config_with_path = DEFAULT_ONTOLOGY_SETTINGS.copy()
            if default_config_with_path.get("ontology_file"):
                 default_config_with_path["ontology_file_path"] = os.path.join(ONTOLOGIES_DIR, default_config_with_path["ontology_file"])
            return default_config_with_path
    elif any(config_or_owl_filename.lower().endswith(f".{ext}") for ext in ["owl", "ttl", "rdf", "xml"]):
        # Gerar configuração a partir do nome do ficheiro de ontologia
        try:
            print(f"A gerar configuração a partir do ficheiro de ontologia: {config_or_owl_filename}")
            return generate_config_from_owl(config_or_owl_filename)
        except FileNotFoundError as e:
            print(f"Erro: {e}. A usar config default.")
            default_config_with_path = DEFAULT_ONTOLOGY_SETTINGS.copy()
            if default_config_with_path.get("ontology_file"):
                 default_config_with_path["ontology_file_path"] = os.path.join(ONTOLOGIES_DIR, default_config_with_path["ontology_file"])
            return default_config_with_path
    else:
        # Nome de ficheiro inválido ou não reconhecido
        print(f"Aviso: Nome de ficheiro '{config_or_owl_filename}' não reconhecido como JSON ou ficheiro de ontologia. A usar config default.")
        default_config_with_path = DEFAULT_ONTOLOGY_SETTINGS.copy()
        if default_config_with_path.get("ontology_file"):
             default_config_with_path["ontology_file_path"] = os.path.join(ONTOLOGIES_DIR, default_config_with_path["ontology_file"])
        return default_config_with_path

# Carregar a configuração ativa inicial (pode ser JSON ou OWL)
ACTIVE_CONFIG = load_ontology_config()

# Para acesso direto às configurações carregadas:
# (Atualizar estas variáveis sempre que ACTIVE_CONFIG mudar)
def update_global_config_vars():
    global ONTOLOGY_FILE_PATH, RDF_BASE_URI, PREFIXES, ITEM_CLASS, TITLE_PROPERTY, AUTHOR_PROPERTY, DESCRIPTION_PROPERTY
    ONTOLOGY_FILE_PATH = ACTIVE_CONFIG.get("ontology_file_path")
    RDF_BASE_URI = ACTIVE_CONFIG.get("RDF_BASE_URI")
    PREFIXES = ACTIVE_CONFIG.get("PREFIXES")
    ITEM_CLASS = ACTIVE_CONFIG.get("ITEM_CLASS")
    TITLE_PROPERTY = ACTIVE_CONFIG.get("TITLE_PROPERTY")
    AUTHOR_PROPERTY = ACTIVE_CONFIG.get("AUTHOR_PROPERTY")
    DESCRIPTION_PROPERTY = ACTIVE_CONFIG.get("DESCRIPTION_PROPERTY")

update_global_config_vars() # Chamar uma vez na inicialização

if __name__ == '__main__':
    print("\nConfiguração da Ontologia Ativa Inicial:")
    for key, value in ACTIVE_CONFIG.items():
        print(f"  {key}: {value}")

    print("\nTestando a deteção de ficheiros de ontologia:")
    available_files = find_available_ontology_files()
    print(f"Ficheiros disponíveis: {available_files}")

    # Testar carregamento por nome de ficheiro OWL (assumindo que existe um 'minha_ontologia.owl')
    # try:
    #     print("\nTestando carregamento por nome OWL:")
    #     owl_config = load_ontology_config("minha_ontologia.owl")
    #     for key, value in owl_config.items():
    #         print(f"  {key}: {value}")
    # except FileNotFoundError:
    #     print("  (Ficheiro 'minha_ontologia.owl' não encontrado para teste)")

    # Testar carregamento por nome JSON (assumindo que existe 'default_ontology_props.json')
    # try:
    #     print("\nTestando carregamento por nome JSON:")
    #     json_config = load_ontology_config("default_ontology_props.json")
    #     for key, value in json_config.items():
    #         print(f"  {key}: {value}")
    # except FileNotFoundError:
    #     print("  (Ficheiro 'default_ontology_props.json' não encontrado para teste)")


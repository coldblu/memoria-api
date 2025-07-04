# Exemplo de configuração para integração com o backend SPARQL
# Copie este arquivo para config/sparql_api_config.py e ajuste conforme necessário

# URL base da API REST do backend SPARQL
API_BASE_URL = "http://localhost:8000"

# URL do endpoint SPARQL de atualização
REPOSITORY_UPDATE_URL = "http://localhost:3030/mydataset/update"

# URI base para os objetos no repositório
REPOSITORY_BASE_URI = "http://localhost:3030/mydataset#"

# Credenciais para autenticação (opcional)
# Se não fornecidas, algumas operações podem falhar
API_EMAIL = "usuario@exemplo.com"
API_PASSWORD = "senha123"

# URI do tipo padrão para objetos catalogados
DEFAULT_TIPO_URI = "http://guara.ueg.br/ontologias/v1/objetos#Documento"

# Mapeamento de campos do item para campos da API
FIELD_MAPPING = {
    "title": "titulo",
    "description": "descricao",
    "author": "autor",  # Será adicionado como relação
    "date": "data",     # Será adicionado como relação
    "location": "local" # Será adicionado como relação
}

# Configuração completa para o RDFStoreInterface
SPARQL_API_CONFIG = {
    "api_base_url": API_BASE_URL,
    "repository_update_url": REPOSITORY_UPDATE_URL,
    "repository_base_uri": REPOSITORY_BASE_URI,
    "email": API_EMAIL,
    "password": API_PASSWORD,
    "default_tipo_uri": DEFAULT_TIPO_URI,
    "field_mapping": FIELD_MAPPING
}

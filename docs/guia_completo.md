# Guia Completo do Agente Catalogador IA

## Índice

1. [Introdução](#introdução)
2. [Requisitos do Sistema](#requisitos-do-sistema)
3. [Instalação](#instalação)
4. [Configuração](#configuração)
   - [Configuração Básica](#configuração-básica)
   - [Configuração de Ontologias](#configuração-de-ontologias)
   - [Configuração da Integração SPARQL](#configuração-da-integração-sparql)
   - [Configuração da IA Local (Ollama)](#configuração-da-ia-local-ollama)
5. [Uso da API](#uso-da-api)
   - [Documentação Swagger](#documentação-swagger)
   - [Endpoints Principais](#endpoints-principais)
   - [Exemplos de Requisições](#exemplos-de-requisições)
6. [Gestão de Ontologias](#gestão-de-ontologias)
   - [Listar Ontologias Disponíveis](#listar-ontologias-disponíveis)
   - [Carregar Novas Ontologias](#carregar-novas-ontologias)
   - [Ativar uma Ontologia](#ativar-uma-ontologia)
7. [Catalogação de Itens](#catalogação-de-itens)
   - [Processo de Catalogação](#processo-de-catalogação)
   - [Formato dos Dados](#formato-dos-dados)
   - [Exemplos de Catalogação](#exemplos-de-catalogação)
8. [Integração com Backend SPARQL](#integração-com-backend-sparql)
   - [Autenticação](#autenticação)
   - [Mapeamento de Triplos para Objetos Dimensionais](#mapeamento-de-triplos-para-objetos-dimensionais)
   - [Fluxo de Dados](#fluxo-de-dados)
9. [Integração com Chatbot](#integração-com-chatbot)
   - [Configuração do Chatbot](#configuração-do-chatbot)
   - [Processamento de Consultas](#processamento-de-consultas)
10. [Processamento de Documentos](#processamento-de-documentos)
    - [OCR](#ocr)
    - [NLP](#nlp)
11. [Troubleshooting](#troubleshooting)
    - [Problemas Comuns](#problemas-comuns)
    - [Logs](#logs)
12. [Desenvolvimento e Extensão](#desenvolvimento-e-extensão)
    - [Arquitetura do Sistema](#arquitetura-do-sistema)
    - [Adição de Novos Componentes](#adição-de-novos-componentes)
13. [Referências](#referências)

## Introdução

O Agente Catalogador IA é uma solução completa para catalogação de acervos para preservação de património cultural. Ele permite catalogar itens, enriquecer dados com referências, persistir informações em formato RDF e integrar-se com sistemas externos.

Este guia fornece instruções detalhadas para instalação, configuração e uso do Agente Catalogador IA, cobrindo todos os aspectos do sistema.

## Requisitos do Sistema

- Python 3.8 ou superior
- Pip (gerenciador de pacotes Python)
- Acesso à internet (para instalação de dependências)
- Opcional: Servidor SPARQL para persistência de dados (ex: Fuseki, GraphDB)
- Opcional: Ollama para IA local

## Instalação

1. **Extraia o arquivo ZIP** do Agente Catalogador IA para um diretório de sua escolha.

2. **Crie um ambiente virtual** (recomendado para evitar conflitos de dependências):
   ```bash
   python -m venv venv_agente
   ```

3. **Ative o ambiente virtual**:
   - Windows: `venv_agente\Scripts\activate`
   - Linux/macOS: `source venv_agente/bin/activate`

4. **Instale as dependências**:
   ```bash
   pip install -r requirements_pinned.txt
   ```

5. **Instale o modelo spaCy** (opcional, para funcionalidades NLP):
   ```bash
   python -m spacy download pt_core_news_sm
   ```

6. **Instale o Tesseract OCR** (opcional, para funcionalidades OCR):
   - Windows: Baixe o instalador em https://github.com/UB-Mannheim/tesseract/wiki
   - Linux: `sudo apt-get install tesseract-ocr`
   - macOS: `brew install tesseract`

## Configuração

### Configuração Básica

O arquivo principal de configuração é `config/settings.py`. Ele contém configurações gerais do sistema, como:

```python
# Diretório para upload de arquivos
UPLOAD_FOLDER = os.path.join(os.path.dirname(os.path.dirname(__file__)), "uploads")

# Porta do servidor
PORT = 5000

# Host do servidor
HOST = "localhost"

# Configurações de logging
LOG_LEVEL = "INFO"
```

### Configuração de Ontologias

As ontologias são configuradas no arquivo `config/ontology_config.py`. O sistema suporta a detecção automática de arquivos de ontologia (.owl, .ttl, .rdf) na pasta `ontologies/`.

Para configurar uma ontologia manualmente:

1. Crie um arquivo JSON na pasta `ontologies/` (ex: `minha_ontologia.json`) com o seguinte conteúdo:
   ```json
   {
     "ontology_file": "minha_ontologia.owl",
     "ontology_format": "owl",
     "RDF_BASE_URI": "http://seusite.org/ontologia#",
     "DEFAULT_ITEM_CLASS": "ClassePrincipalDaSuaOntologia",
     "PROPERTY_MAP": {
       "title": "dcterms:title",
       "author": "dcterms:creator"
     }
   }
   ```

2. Ative a ontologia através da API (ver seção [Ativar uma Ontologia](#ativar-uma-ontologia)).

### Configuração da Integração SPARQL

Para integrar com o backend SPARQL:

1. Copie o arquivo `config/sparql_api_config_example.py` para `config/sparql_api_config.py`.

2. Edite o arquivo com as configurações do seu ambiente:
   ```python
   # URL base da API REST do backend SPARQL
   API_BASE_URL = "http://localhost:8000"

   # URL do endpoint SPARQL de atualização
   REPOSITORY_UPDATE_URL = "http://localhost:3030/mydataset/update"

   # URI base para os objetos no repositório
   REPOSITORY_BASE_URI = "http://localhost:3030/mydataset#"

   # Credenciais para autenticação
   API_EMAIL = "usuario@exemplo.com"
   API_PASSWORD = "senha123"

   # URI do tipo padrão para objetos catalogados
   DEFAULT_TIPO_URI = "http://guara.ueg.br/ontologias/v1/objetos#Documento"
   ```

### Configuração da IA Local (Ollama)

Para usar IA local com Ollama:

1. Instale o Ollama seguindo as instruções em https://ollama.ai/

2. Copie o arquivo `llm_integration/ollama_config_example.json` para `llm_integration/ollama_config.json`.

3. Edite o arquivo com as configurações do seu ambiente:
   ```json
   {
     "base_url": "http://localhost:11434",
     "model": "llama2",
     "temperature": 0.7,
     "max_tokens": 1000
   }
   ```

## Uso da API

### Documentação Swagger

O Agente Catalogador IA fornece uma documentação interativa da API através do Swagger UI. Para acessá-la:

1. Inicie o servidor:
   ```bash
   python main.py
   ```

2. Acesse a documentação em seu navegador:
   ```
   http://localhost:5000/docs
   ```

### Endpoints Principais

Os principais endpoints da API são:

- **GET /api/v1/config/ontologies/available**: Lista as ontologias disponíveis.
- **POST /api/v1/config/ontologies/upload**: Carrega uma nova ontologia.
- **PUT /api/v1/config/ontology**: Ativa uma ontologia.
- **POST /api/v1/catalog/item**: Cataloga um novo item.
- **GET /api/v1/catalog/items**: Lista itens catalogados.
- **POST /api/v1/chatbot/query**: Envia uma consulta ao chatbot.
- **POST /api/v1/documents/process**: Processa um documento.

### Exemplos de Requisições

#### Listar Ontologias Disponíveis

```bash
curl -X GET http://localhost:5000/api/v1/config/ontologies/available
```

#### Catalogar um Item

```bash
curl -X POST http://localhost:5000/api/v1/catalog/item \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Manuscrito Antigo",
    "author": "Autor Desconhecido",
    "description": "Um manuscrito raro do século XVIII",
    "date": "1750",
    "location": "Lisboa, Portugal"
  }'
```

## Gestão de Ontologias

### Listar Ontologias Disponíveis

Para listar as ontologias disponíveis:

```bash
curl -X GET http://localhost:5000/api/v1/config/ontologies/available
```

Resposta:
```json
{
  "ontology_files": [
    "default_ontology_props.json",
    "exemplo_ontologia.ttl",
    "minha_ontologia.owl"
  ]
}
```

### Carregar Novas Ontologias

Para carregar uma nova ontologia:

```bash
curl -X POST -F "ontology_file=@/caminho/para/sua/nova_ontologia.owl" \
  http://localhost:5000/api/v1/config/ontologies/upload
```

Resposta:
```json
{
  "message": "Ontologia carregada com sucesso",
  "filename": "nova_ontologia.owl"
}
```

### Ativar uma Ontologia

Para ativar uma ontologia:

```bash
curl -X PUT -H "Content-Type: application/json" \
  -d '{"ontology_identifier": "minha_ontologia.owl"}' \
  http://localhost:5000/api/v1/config/ontology
```

Resposta:
```json
{
  "message": "Ontologia ativada com sucesso",
  "ontology": "minha_ontologia.owl",
  "config": {
    "ontology_file": "minha_ontologia.owl",
    "ontology_format": "owl",
    "RDF_BASE_URI": "http://example.org/ontology#",
    "DEFAULT_ITEM_CLASS": "Document"
  }
}
```

## Catalogação de Itens

### Processo de Catalogação

O processo de catalogação envolve as seguintes etapas:

1. **Recebimento dos dados**: O sistema recebe os dados do item a ser catalogado.
2. **Enriquecimento**: O sistema enriquece os dados com referências (se o ReferenceLinker estiver disponível).
3. **Mapeamento para RDF**: Os dados são mapeados para triplos RDF de acordo com a ontologia ativa.
4. **Persistência**: Os triplos RDF são persistidos no repositório SPARQL (se configurado).

### Formato dos Dados

Os dados do item devem ser fornecidos em formato JSON, com campos como:

```json
{
  "title": "Título do Item",
  "author": "Autor do Item",
  "description": "Descrição do Item",
  "date": "Data do Item",
  "location": "Localização do Item",
  "type": "Tipo do Item",
  "media": ["URL da Mídia 1", "URL da Mídia 2"]
}
```

### Exemplos de Catalogação

#### Catalogar um Manuscrito

```bash
curl -X POST http://localhost:5000/api/v1/catalog/item \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Manuscrito Antigo",
    "author": "Autor Desconhecido",
    "description": "Um manuscrito raro do século XVIII",
    "date": "1750",
    "location": "Lisboa, Portugal",
    "type": "Manuscrito",
    "media": ["http://example.org/media/manuscrito.jpg"]
  }'
```

#### Catalogar uma Pintura

```bash
curl -X POST http://localhost:5000/api/v1/catalog/item \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Paisagem Marítima",
    "author": "João Silva",
    "description": "Uma pintura a óleo retratando uma paisagem marítima",
    "date": "1850",
    "location": "Porto, Portugal",
    "type": "Pintura",
    "media": ["http://example.org/media/pintura.jpg"]
  }'
```

## Integração com Backend SPARQL

### Autenticação

A autenticação com o backend SPARQL é realizada automaticamente quando o SPARQLAPIClient é inicializado com credenciais. O token JWT é armazenado e utilizado em todas as requisições subsequentes.

```python
from storage.sparql_api_client import SPARQLAPIClient

client = SPARQLAPIClient(
    api_base_url="http://localhost:8000",
    repository_update_url="http://localhost:3030/mydataset/update",
    repository_base_uri="http://localhost:3030/mydataset#",
    email="usuario@exemplo.com",
    password="senha123"
)

# A autenticação é realizada automaticamente
```

### Mapeamento de Triplos para Objetos Dimensionais

O RDFStoreInterface mapeia triplos RDF para objetos dimensionais da seguinte forma:

- Triplos com predicados relacionados a título são mapeados para o campo `titulo`
- Triplos com predicados relacionados a descrição são mapeados para `resumo` ou `descricao`
- Triplos com predicados relacionados a tipo são mapeados para `tipo_uri`
- Triplos com predicados relacionados a mídia são mapeados para `associatedMedia`
- Triplos com predicados relacionados a relações são mapeados para `temRelacao`
- Outros triplos são adicionados como relações individuais após a criação do objeto

### Fluxo de Dados

O fluxo de dados na integração com o backend SPARQL é o seguinte:

1. O Cataloger recebe os dados do item a ser catalogado.
2. O Cataloger mapeia os dados para triplos RDF de acordo com a ontologia ativa.
3. O Cataloger chama o RDFStoreInterface para persistir os triplos.
4. O RDFStoreInterface mapeia os triplos para objetos dimensionais.
5. O SPARQLAPIClient envia os objetos dimensionais para o backend SPARQL.
6. O backend SPARQL persiste os objetos no repositório.

## Integração com Chatbot

### Configuração do Chatbot

O Agente Catalogador IA inclui um serviço de chatbot que pode ser integrado com sistemas externos. Para configurar o chatbot:

1. Edite o arquivo `config/settings.py` para definir as configurações do chatbot:
   ```python
   # Configurações do chatbot
   CHATBOT_MODEL = "gpt-3.5-turbo"  # ou "ollama" para IA local
   CHATBOT_TEMPERATURE = 0.7
   CHATBOT_MAX_TOKENS = 1000
   ```

2. Se estiver usando IA local (Ollama), configure o arquivo `llm_integration/ollama_config.json` conforme descrito na seção [Configuração da IA Local (Ollama)](#configuração-da-ia-local-ollama).

### Processamento de Consultas

Para enviar uma consulta ao chatbot:

```bash
curl -X POST http://localhost:5000/api/v1/chatbot/query \
  -H "Content-Type: application/json" \
  -d '{
    "query": "Quem é o autor do Manuscrito Antigo?",
    "context": {
      "item_id": "123",
      "user_id": "456"
    }
  }'
```

Resposta:
```json
{
  "response": "O autor do Manuscrito Antigo é desconhecido, conforme registrado em nossa base de dados.",
  "sources": [
    {
      "item_id": "123",
      "title": "Manuscrito Antigo",
      "author": "Autor Desconhecido"
    }
  ]
}
```

## Processamento de Documentos

### OCR

O Agente Catalogador IA inclui funcionalidades de OCR (Reconhecimento Óptico de Caracteres) para extrair texto de imagens. Para usar o OCR:

```bash
curl -X POST -F "file=@/caminho/para/sua/imagem.jpg" \
  http://localhost:5000/api/v1/documents/ocr
```

Resposta:
```json
{
  "text": "Texto extraído da imagem",
  "confidence": 0.95
}
```

### NLP

O Agente Catalogador IA inclui funcionalidades de NLP (Processamento de Linguagem Natural) para analisar texto. Para usar o NLP:

```bash
curl -X POST -H "Content-Type: application/json" \
  -d '{"text": "Este é um texto de exemplo para análise."}' \
  http://localhost:5000/api/v1/documents/nlp
```

Resposta:
```json
{
  "entities": [
    {
      "text": "texto de exemplo",
      "label": "MISC",
      "start": 9,
      "end": 25
    }
  ],
  "tokens": [
    "Este", "é", "um", "texto", "de", "exemplo", "para", "análise", "."
  ]
}
```

## Troubleshooting

### Problemas Comuns

#### Erro de Autenticação com o Backend SPARQL

**Problema**: Falha na autenticação com o backend SPARQL.

**Solução**:
1. Verifique se as credenciais em `config/sparql_api_config.py` estão corretas.
2. Verifique se o backend SPARQL está acessível no URL especificado.
3. Verifique os logs para mais detalhes sobre o erro.

#### Erro ao Carregar Ontologia

**Problema**: Falha ao carregar ou ativar uma ontologia.

**Solução**:
1. Verifique se o arquivo da ontologia existe na pasta `ontologies/`.
2. Verifique se o formato do arquivo é suportado (.owl, .ttl, .rdf, .xml, .json).
3. Verifique se o arquivo está bem formado e não contém erros de sintaxe.

#### Erro de OCR

**Problema**: Falha ao extrair texto de imagens.

**Solução**:
1. Verifique se o Tesseract OCR está instalado corretamente.
2. Verifique se a imagem é legível e tem boa qualidade.
3. Tente pré-processar a imagem para melhorar a qualidade antes de usar o OCR.

### Logs

Os logs do sistema são armazenados no console por padrão. Para salvar os logs em um arquivo:

1. Edite o arquivo `config/settings.py` para configurar o logging:
   ```python
   # Configurações de logging
   LOG_LEVEL = "INFO"
   LOG_FILE = "agente_catalogador.log"
   ```

2. Reinicie o servidor para aplicar as alterações.

## Desenvolvimento e Extensão

### Arquitetura do Sistema

O Agente Catalogador IA é organizado em módulos:

- **core/**: Contém os componentes principais do sistema.
  - **agent.py**: Agente principal que coordena os outros componentes.
  - **cataloger.py**: Responsável pela catalogação de itens.
  - **reference_linker.py**: Responsável por encontrar e ligar referências.
  - **data_acquirer.py**: Responsável por adquirir dados de várias fontes.
  - **search_engine.py**: Responsável por realizar buscas.
  - **chatbot_service.py**: Serviço de chatbot.
  - **document_processor_service.py**: Serviço de processamento de documentos.

- **apis/**: Contém clientes para APIs internas e externas.
  - **internal_api_client.py**: Cliente para APIs internas.
  - **external_ia_clients.py**: Cliente para APIs externas de IA.

- **storage/**: Contém interfaces para armazenamento de dados.
  - **rdf_store_interface.py**: Interface para o repositório RDF.
  - **database_connector.py**: Conector para banco de dados.
  - **sparql_api_client.py**: Cliente para a API SPARQL.

- **config/**: Contém arquivos de configuração.
  - **settings.py**: Configurações gerais do sistema.
  - **ontology_config.py**: Configurações de ontologias.
  - **sparql_api_config.py**: Configurações da API SPARQL.

- **ontologies/**: Contém arquivos de ontologia.

- **llm_integration/**: Contém integração com modelos de linguagem.
  - **ollama_client.py**: Cliente para Ollama.

- **chatbot_integration/**: Contém integração com chatbots.
  - **handler.py**: Manipulador de requisições de chatbot.

- **docs/**: Contém documentação.

- **tests/**: Contém testes unitários.

### Adição de Novos Componentes

Para adicionar um novo componente ao sistema:

1. Crie um novo arquivo Python no diretório apropriado.
2. Implemente a classe ou função necessária.
3. Importe e use o componente onde necessário.
4. Adicione testes unitários para o componente.
5. Atualize a documentação.

Exemplo de adição de um novo serviço:

```python
# core/novo_servico.py
class NovoServico:
    def __init__(self, config=None):
        self.config = config or {}
        print("NovoServico inicializado.")

    def processar(self, dados):
        print(f"Processando dados: {dados}")
        # Lógica de processamento aqui
        return {"resultado": "Dados processados com sucesso"}
```

## Referências

- [Documentação do FastAPI](https://fastapi.tiangolo.com/)
- [Documentação do RDFLib](https://rdflib.readthedocs.io/)
- [Documentação do spaCy](https://spacy.io/api/doc)
- [Documentação do Tesseract OCR](https://tesseract-ocr.github.io/)
- [Documentação do Ollama](https://ollama.ai/docs)
- [Especificação OpenAPI](https://swagger.io/specification/)

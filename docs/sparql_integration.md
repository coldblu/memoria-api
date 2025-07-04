# Documentação de Integração com Backend SPARQL

## Visão Geral

Este documento descreve como o Agente Catalogador IA foi integrado com o backend SPARQL (Guará API) para persistência real de dados RDF, substituindo a simulação anterior.

## Arquitetura da Integração

A integração foi implementada através de dois componentes principais:

1. **SPARQLAPIClient** (`storage/sparql_api_client.py`): Cliente dedicado para comunicação com a API REST do backend SPARQL, implementando autenticação JWT e métodos para criar objetos dimensionais, adicionar relações e outras operações.

2. **RDFStoreInterface Adaptado** (`storage/rdf_store_interface.py`): A interface existente foi adaptada para utilizar o SPARQLAPIClient, mantendo a compatibilidade com o restante do sistema.

## Configuração

Para configurar a integração:

1. Copie o arquivo `config/sparql_api_config_example.py` para `config/sparql_api_config.py`
2. Edite o arquivo `config/sparql_api_config.py` com as configurações do seu ambiente:
   - `API_BASE_URL`: URL base da API REST do backend SPARQL
   - `REPOSITORY_UPDATE_URL`: URL do endpoint SPARQL de atualização
   - `REPOSITORY_BASE_URI`: URI base para os objetos no repositório
   - `API_EMAIL` e `API_PASSWORD`: Credenciais para autenticação
   - `DEFAULT_TIPO_URI`: URI do tipo padrão para objetos catalogados

## Uso no Código

Para utilizar a integração no código:

```python
from storage.rdf_store_interface import RDFStoreInterface
from config.sparql_api_config import SPARQL_API_CONFIG

# Criar a interface RDF com a configuração
rdf_store = RDFStoreInterface(SPARQL_API_CONFIG)

# Adicionar triplos (serão convertidos para objetos dimensionais)
triples = [
    ("http://example.org/item/123", "http://schema.org/title", "Manuscrito Antigo"),
    ("http://example.org/item/123", "http://schema.org/description", "Um manuscrito raro do século XVIII"),
    ("http://example.org/item/123", "http://www.w3.org/1999/02/22-rdf-syntax-ns#type", "http://guara.ueg.br/ontologias/v1/objetos#Documento")
]

result = rdf_store.add_triples(triples)
print(f"Objeto criado: {result}")
```

## Mapeamento de Triplos para Objetos Dimensionais

O RDFStoreInterface mapeia triplos RDF para objetos dimensionais da seguinte forma:

- Triplos com predicados relacionados a título são mapeados para o campo `titulo`
- Triplos com predicados relacionados a descrição são mapeados para `resumo` ou `descricao`
- Triplos com predicados relacionados a tipo são mapeados para `tipo_uri`
- Triplos com predicados relacionados a mídia são mapeados para `associatedMedia`
- Triplos com predicados relacionados a relações são mapeados para `temRelacao`
- Outros triplos são adicionados como relações individuais após a criação do objeto

## Autenticação

A autenticação é realizada automaticamente quando o SPARQLAPIClient é inicializado com credenciais. O token JWT é armazenado e utilizado em todas as requisições subsequentes.

## Tratamento de Erros

Erros de comunicação com a API são registrados no log e propagados como exceções. O RDFStoreInterface captura essas exceções e retorna um dicionário com informações sobre o erro.

## Limitações Conhecidas

- A consulta SPARQL direta (`query_triples`) não está completamente implementada na API atual
- A exclusão de objetos (`remove_triples`) remove o objeto inteiro, não triplos individuais
- O mapeamento de triplos para objetos dimensionais é simplificado e pode não cobrir todos os casos

## Testes

Testes unitários para a integração estão disponíveis em `tests/test_sparql_integration.py`. Execute-os com:

```bash
python -m unittest tests/test_sparql_integration.py
```

## Próximos Passos

- Implementar mapeamento mais sofisticado de triplos para objetos dimensionais
- Adicionar suporte para consultas SPARQL diretas
- Melhorar o tratamento de erros e recuperação

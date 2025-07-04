# Documentação da API do Agente de Catalogação IA

Este documento descreve os endpoints da API exposta pelo agente, que pode ser utilizada para integração com o chatbot ou outros sistemas.

## Endpoints

(Detalhes dos endpoints, métodos HTTP, parâmetros de entrada e formatos de resposta serão adicionados aqui à medida que a API for desenvolvida.)

### Exemplo de Endpoint (Conceptual)

*   **POST /catalog**
    *   Descrição: Submete um novo item para catalogação.
    *   Corpo da Requisição (JSON):
        ```json
        {
          "item_data": { ... },
          "source_info": { ... }
        }
        ```
    *   Resposta (JSON):
        ```json
        {
          "status": "sucesso",
          "message": "Item catalogado com sucesso.",
          "item_uri": "http://example.org/patrimonio/item/123"
        }
        ```

*   **GET /search**
    *   Descrição: Realiza uma busca no acervo.
    *   Parâmetros de Query:
        *   `query` (string, obrigatório): Termo de busca.
        *   `sources` (string, opcional): Fontes a serem consultadas (ex: "local,web").
    *   Resposta (JSON):
        ```json
        {
          "results": [ ... ]
        }
        ```


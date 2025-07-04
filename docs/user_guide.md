# Guia do Utilizador do Agente de Catalogação IA

Este guia fornece instruções sobre como configurar e utilizar o Agente de Catalogação IA.

## Configuração Inicial

1.  **Clonar o Repositório:**
    (Instruções para clonar o repositório serão adicionadas aqui)

2.  **Instalar Dependências:**
    Navegue até ao diretório do projeto e execute:
    ```bash
    pip install -r requirements.txt
    ```

3.  **Configurar o Agente:**
    *   Edite o ficheiro `config/settings.py` para adicionar as suas chaves de API (para IA externa, backend, etc.) e outros caminhos necessários.
    *   Edite o ficheiro `config/ontology_config.py` para especificar o caminho para o seu ficheiro de ontologia e os prefixos RDF desejados.
    *   Coloque o seu ficheiro de ontologia (ex: `.owl`, `.ttl`) no diretório `ontologies/`.

## Utilização

### Executar o Agente (Modo API)

Para iniciar o agente como um serviço de API (por exemplo, para ser consumido pelo chatbot):
```bash
python main.py
```
Isto irá iniciar um servidor (detalhes a serem definidos, ex: Flask/FastAPI) que expõe os endpoints definidos em `docs/api_reference.md`.

### Interagir via Chatbot

(Instruções sobre como integrar e interagir com o agente através do chatbot do frontend serão adicionadas aqui.)

### Funcionalidades Principais

*   **Catalogar um Item:**
    (Como submeter um item para catalogação, quais dados são necessários, etc.)

*   **Buscar Referências:**
    (Como pedir ao agente para buscar referências para um item ou tópico.)

*   **Consultar o Acervo:**
    (Como realizar buscas no acervo catalogado.)

## Opções de IA

O agente pode ser configurado para usar:
*   **IA Local:** (Detalhes sobre como configurar e usar modelos locais, se disponíveis)
*   **IA Externa (API):** (Detalhes sobre como configurar as chaves de API em `config/settings.py`)

## Resolução de Problemas

(Secção para problemas comuns e as suas soluções será adicionada aqui.)


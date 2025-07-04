# README - Integração com Ollama

Este diretório contém os arquivos necessários para integrar o Agente Catalogador IA com o Ollama, uma ferramenta para executar modelos de linguagem localmente.

## Arquivos

- `ollama_client.py`: Cliente Python para interagir com a API do Ollama
- `ollama_config_example.json`: Exemplo de arquivo de configuração para o cliente Ollama

## Configuração

1. **Instalar o Ollama**:
   - Siga as instruções em [https://ollama.ai/](https://ollama.ai/) para instalar o Ollama no seu sistema
   - O Ollama deve estar em execução na porta padrão 11434

2. **Baixar um modelo**:
   - Após instalar o Ollama, baixe um modelo usando o comando:
     ```
     ollama pull llama2
     ```
   - Você pode substituir "llama2" por qualquer outro modelo suportado

3. **Configurar o cliente**:
   - Copie o arquivo `ollama_config_example.json` para `ollama_config.json`
   - Ajuste os parâmetros conforme necessário:
     - `base_url`: URL da API do Ollama (padrão: http://localhost:11434)
     - `model`: Nome do modelo a ser usado (ex: llama2, mistral, etc.)
     - `parameters`: Parâmetros de geração de texto

## Uso

Para usar o cliente Ollama no seu código:

```python
from llm_integration.ollama_client import OllamaClient

# Inicializar o cliente com configuração personalizada
client = OllamaClient(config_path="llm_integration/ollama_config.json")

# Ou usar configurações padrão
# client = OllamaClient()

# Gerar texto
response = client.generate_text("Explique o que é patrimônio cultural.")
print(response.get("response", ""))

# Usar no formato de chat
chat_response = client.chat_completion([
    {"role": "system", "content": "Você é um assistente especializado em patrimônio cultural."},
    {"role": "user", "content": "O que são bens imateriais?"}
])
print(chat_response.get("message", {}).get("content", ""))
```

## Integração com o Agente Catalogador

Para integrar o Ollama com o chatbot e outros componentes do Agente Catalogador, você precisará:

1. Modificar o `ChatbotService` para usar o `OllamaClient`
2. Atualizar o processamento de documentos para usar o LLM para extração de entidades específicas
3. Implementar RAG (Retrieval Augmented Generation) para consultas baseadas no acervo

Consulte a documentação do projeto para mais detalhes sobre essas integrações.

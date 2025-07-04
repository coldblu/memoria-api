# memoria/core/chatbot_service.py

import os
import requests
import json
import asyncio
from typing import Tuple, Dict, Any, List
from storage.sparql_api_client import SPARQLAPIClient
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class ChatbotService:
    """
    Serviço de chatbot que utiliza RAG (Retrieval-Augmented Generation)
    para responder a perguntas com base nos dados do repositório SPARQL.
    """

    def __init__(self, sparql_client: SPARQLAPIClient):
        self.sparql_client = sparql_client
        self.gemini_api_key = os.getenv("GEMINI_API_KEY")
        if not self.gemini_api_key:
            logger.warning("AVISO: Chave da API do Gemini não encontrada. O Chatbot terá funcionalidade limitada.")

    def _format_sparql_results(self, results: List[Dict[str, Any]]) -> str:
        """Formata os resultados da busca SPARQL para um texto legível e conciso."""
        if not results:
            return "Nenhuma informação específica encontrada na base de dados."

        # Constrói uma string de contexto a partir dos resultados
        context_parts = []
        for item in results:
            titulo = item.get('titulo', {}).get('value', 'N/A')
            resumo = item.get('resumo', {}).get('value', '')
            context_parts.append(f"Item: {titulo}. Detalhes: {resumo}")

        return " ".join(context_parts)

    async def _call_gemini(self, prompt: str) -> str:
        """Chama a API do Gemini com um prompt e retorna a resposta."""
        if not self.gemini_api_key:
            return "Lamento, a funcionalidade de conversação com IA não está configurada no momento."

        api_url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash-latest:generateContent?key={self.gemini_api_key}"
        payload = {
            "contents": [{"parts": [{"text": prompt}]}],
            "generationConfig": {
                "temperature": 0.7,
                "topP": 0.95,
            }
        }

        try:
            loop = asyncio.get_event_loop()
            response = await loop.run_in_executor(
                None,
                lambda: requests.post(api_url, json=payload, timeout=60)
            )
            response.raise_for_status()
            api_result = response.json()
            return api_result['candidates'][0]['content']['parts'][0]['text']
        except Exception as e:
            logger.error(f"Erro ao chamar a API do Gemini: {e}")
            return "Desculpe, ocorreu um erro ao tentar gerar a resposta. Por favor, tente novamente mais tarde."

    async def process_message(self, user_message: str, repository_name: str) -> Tuple[str, List[Dict[str, Any]]]:
        """
        Processa a mensagem do utilizador, aplicando a lógica RAG.
        """
        logger.info(f"Processando mensagem para o repositório '{repository_name}': '{user_message}'")

        repo_config = {
            "repository_query_url": f"http://localhost:3030/{repository_name}/query"
        }

        # 1. Recuperação (Retrieval) - Buscar dados no repositório
        search_results = self.sparql_client.list_objects(user_message, repo_config)
        context_data = self._format_sparql_results(search_results)

        # 2. Geração (Generation) - Construir o prompt para a IA
        prompt = f"""
        Você é 'MemoriA', um assistente de IA especializado em contar histórias sobre património cultural.
        A sua tarefa é responder à pergunta do utilizador de forma envolvente, usando a informação contextual da nossa base de dados.

        Pergunta do Utilizador: "{user_message}"

        Informação da Base de Dados:
        ---
        {context_data}
        ---

        Instruções:
        - Se a pergunta pedir para "contar uma história", crie uma narrativa curta e interessante usando os dados.
        - Se for uma pergunta direta, responda de forma clara e informativa.
        - Se a "Informação da Base de Dados" for "Nenhuma informação específica encontrada", diga ao utilizador que não encontrou detalhes sobre esse tópico no acervo.
        - Seja sempre simpático, criativo e evite respostas demasiado técnicas.

        A sua resposta:
        """

        # 3. Chamar a IA para obter a resposta final
        ai_response = await self._call_gemini(prompt)

        # Retorna a resposta da IA e os dados de origem para o frontend
        return ai_response, search_results


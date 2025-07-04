# memoria/core/persistence_service.py
import asyncio
from typing import List, Dict, Any
from config import ontology_config  # Para aceder às propriedades da ontologia
from storage.sparql_api_client import SPARQLAPIClient
import logging
#from aiohttp import ClientSession

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class PersistenceService:
    """
    Gerencia uma fila para salvar itens catalogados de forma assíncrona,
    verificando duplicados e preparando para futuras relações.
    """

    def __init__(self, sparql_api_client: SPARQLAPIClient):
        self.queue = asyncio.Queue()
        self.sparql_client = sparql_api_client
        self.worker_task = None
        self.processing_status = {}  # Guarda o status por ID de tarefa

    def start_worker(self):
        """Inicia a tarefa de fundo (worker) para processar a fila."""
        if not self.worker_task or self.worker_task.done():
            self.worker_task = asyncio.create_task(self._process_queue())
            logger.info("Worker do serviço de persistência iniciado.")

    async def add_to_queue(self, items: List[Dict[str, Any]], repo_config: Dict[str, str], task_id: str):
        """Adiciona uma lista de itens e a configuração do repositório à fila."""
        await self.queue.put((items, repo_config, task_id))
        self.processing_status[task_id] = {
            "status": "pending",
            "total_items": len(items),
            "processed_items": 0,
            "results": []
        }
        logger.info(f"Tarefa {task_id} com {len(items)} itens adicionada à fila de persistência.")

    async def _process_queue(self):
        """Processa continuamente os itens da fila."""
        while True:
            items, repo_config, task_id = await self.queue.get()
            self.processing_status[task_id]['status'] = 'processing'
            logger.info(f"Iniciando processamento da tarefa de persistência {task_id}.")

            try:
                for item in items:
                    # Pequeno delay para não sobrecarregar a API Guará
                    await asyncio.sleep(0.5)

                    title = item.get("properties", {}).get(ontology_config.TITLE_PROPERTY)
                    if not title:
                        self._log_result(task_id, item, "error", "Item sem título não pode ser processado.")
                        continue

                    # 1. Verificar duplicados através da API Guará
                    logger.info(f"Verificando duplicados para: '{title}'")
                    existing_items = self.sparql_client.list_objects(title, repo_config)

                    if existing_items:
                        # 2a. Se existe, regista como duplicado
                        existing_uri = existing_items[0].get("obj", {}).get("value")
                        message = f"Item já existe no repositório. URI: {existing_uri}"
                        self._log_result(task_id, item, "duplicate", message, existing_uri)
                    else:
                        # 2b. Se não existe, cria o novo item
                        payload = self._prepare_payload(item)
                        result = self.sparql_client.create_dimensional_object(payload, repo_config)
                        new_uri = result.get("object_uri")
                        self._log_result(task_id, item, "created", f"Item criado com sucesso.", new_uri)

            except Exception as e:
                self.processing_status[task_id]['status'] = 'failed'
                self.processing_status[task_id]['error'] = str(e)
                logger.error(f"Falha ao processar a tarefa {task_id}: {e}")

            if self.processing_status[task_id]['status'] != 'failed':
                self.processing_status[task_id]['status'] = 'completed'

            logger.info(f"Processamento da tarefa {task_id} concluído.")
            self.queue.task_done()

    def _log_result(self, task_id, item, status, message, uri=None):
        """Regista o resultado do processamento de um único item."""
        self.processing_status[task_id]["processed_items"] += 1
        self.processing_status[task_id]["results"].append({
            "item_title": item.get("properties", {}).get(ontology_config.TITLE_PROPERTY, "Título desconhecido"),
            "status": status,
            "message": message,
            "uri": uri
        })

    def _prepare_payload(self, item: Dict[str, Any]) -> Dict[str, Any]:
        """Converte o formato do item extraído para o formato esperado pela API Guará."""
        props = item.get("properties", {})
        # Mapeia as propriedades da ontologia para as chaves esperadas pela API Guará
        return {
            "titulo": props.get(ontology_config.TITLE_PROPERTY),
            "resumo": props.get(ontology_config.DESCRIPTION_PROPERTY, "Sem resumo."),
            "descricao": props.get(ontology_config.DESCRIPTION_PROPERTY),
            "tipo_uri": item.get("entry_type")
            # Futuramente, poderia adicionar outros campos como:
            # "temRelacao": [uri_do_autor, uri_do_local]
        }

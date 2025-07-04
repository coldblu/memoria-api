# memoria/storage/sparql_api_client.py
"""
Cliente para interagir com a API REST do backend SPARQL (Guará API).
"""
import requests
import logging
from typing import Dict, List, Any, Optional

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class SPARQLAPIClient:
    """
    Cliente para interagir com a API REST do backend SPARQL (Guará API).
    Implementa autenticação JWT e métodos para criar e consultar objetos.
    """

    def __init__(self,
                 api_base_url: str,
                 email: Optional[str] = None,
                 password: Optional[str] = None):
        self.api_base_url = api_base_url.rstrip('/')
        self.email = email
        self.password = password
        self.token = None

        if email and password:
            self.authenticate()

    def authenticate(self) -> bool:
        """Autentica o cliente e armazena o token."""
        if not self.email or not self.password:
            logger.warning("Credenciais para a API Guará não fornecidas.")
            return False

        try:
            login_url = f"{self.api_base_url}/acesso/login"
            payload = {"email": self.email, "password": self.password}
            response = requests.post(login_url, json=payload, timeout=15)
            response.raise_for_status()

            data = response.json()
            self.token = data.get("token")

            if self.token:
                logger.info("Autenticação com a API Guará bem-sucedida.")
                return True
            return False

        except requests.exceptions.RequestException as e:
            logger.error(f"Erro na autenticação com a API Guará: {e}")
            return False

    def _get_headers(self) -> Dict[str, str]:
        """Constrói os cabeçalhos HTTP com o token de autenticação."""
        headers = {"Content-Type": "application/json"}
        if self.token:
            headers["Authorization"] = f"Bearer {self.token}"
        return headers

    def create_dimensional_object(self, item_data: Dict[str, Any], repo_config: Dict[str, str]) -> Dict[str, Any]:
        """Cria um novo objeto dimensional no repositório."""
        try:
            endpoint = f"{self.api_base_url}/dim/create"
            # Combina os dados do item com a configuração do repositório (URLs, etc.)
            payload = {**item_data, **repo_config}

            response = requests.post(endpoint, json=payload, headers=self._get_headers(), timeout=30)
            response.raise_for_status()

            result = response.json()
            logger.info(f"Objeto dimensional criado via API Guará: {result.get('object_uri')}")
            return result

        except requests.exceptions.RequestException as e:
            logger.error(f"Erro ao criar objeto dimensional na API Guará: {e}")
            if hasattr(e, 'response') and e.response:
                logger.error(f"Detalhes do erro da API Guará: {e.response.text}")
            raise

    def list_objects(self, keyword: str, repo_config: Dict[str, str]) -> List[Dict[str, Any]]:
        """Busca por objetos existentes usando uma palavra-chave."""
        try:
            endpoint = f"{self.api_base_url}/dim/list"
            payload = {
                "keyword": keyword,
                "repository": repo_config.get("repository_query_url")  # Usa o endpoint de consulta
            }
            response = requests.post(endpoint, json=payload, headers=self._get_headers(), timeout=30)
            response.raise_for_status()

            result = response.json()
            bindings = result.get("results", {}).get("bindings", [])
            logger.info(f"Busca por '{keyword}' na API Guará encontrou {len(bindings)} resultados.")
            return bindings

        except requests.exceptions.RequestException as e:
            logger.error(f"Erro ao listar objetos na API Guará: {e}")
            return []

    def list_repositories(self) -> List[Dict[str, Any]]:
        """Busca a lista de repositórios disponíveis na API Guará."""
        try:
            endpoint = f"{self.api_base_url}/repositorios/listar_repositorios"
            response = requests.get(endpoint, headers=self._get_headers(), timeout=15)
            response.raise_for_status()

            result = response.json()
            logger.info("Lista de repositórios obtida da API Guará.")
            return result.get("results", {}).get("bindings", [])

        except requests.exceptions.RequestException as e:
            logger.error(f"Erro ao listar repositórios da API Guará: {e}")
            return []


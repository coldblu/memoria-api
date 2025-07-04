# Interface para interagir com o repositório RDF (ex: Triple Store).
from typing import List, Dict, Any, Tuple, Optional, Union
import logging
from .sparql_api_client import SPARQLAPIClient

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class RDFStoreInterface:
    """
    Interface para interagir com o repositório RDF através da API REST do backend SPARQL.
    Esta classe serve como adaptador entre o Cataloger e o SPARQLAPIClient.
    """
    
    def __init__(self, config: Dict[str, Any]):
        """
        Inicializa a interface com o repositório RDF.
        
        Args:
            config: Dicionário de configuração contendo:
                - api_base_url: URL base da API REST
                - repository_update_url: URL do endpoint SPARQL de atualização
                - repository_base_uri: URI base para os objetos no repositório
                - email: Email para autenticação (opcional)
                - password: Senha para autenticação (opcional)
                - default_tipo_uri: URI do tipo padrão para objetos (opcional)
        """
        self.config = config
        self.default_tipo_uri = config.get('default_tipo_uri', 'http://guara.ueg.br/ontologias/v1/objetos#Documento')
        
        # Inicializar o cliente da API SPARQL
        self.api_client = SPARQLAPIClient(
            api_base_url=config.get('api_base_url', 'http://localhost:8000'),
            repository_update_url=config.get('repository_update_url', ''),
            repository_base_uri=config.get('repository_base_uri', ''),
            email=config.get('email'),
            password=config.get('password')
        )
        
        # Tentar autenticar se credenciais foram fornecidas
        if config.get('email') and config.get('password'):
            self.api_client.authenticate()
        else:
            logger.warning("Credenciais não fornecidas. Algumas operações podem falhar.")

    def add_triples(self, triples_list: List[Tuple[str, str, str]]) -> Dict[str, Any]:
        """
        Adiciona uma lista de triplos ao repositório.
        Esta implementação é simplificada e assume que os triplos estão relacionados a um único objeto.
        
        Args:
            triples_list: Lista de triplos no formato [(sujeito, predicado, objeto), ...]
            
        Returns:
            Dict[str, Any]: Resposta da API contendo a URI do objeto criado.
        """
        if not triples_list:
            logger.warning("Lista de triplos vazia. Nada a adicionar.")
            return {"status": "error", "message": "Lista de triplos vazia"}
        
        # Extrair informações do primeiro triplo (assumindo que todos os triplos têm o mesmo sujeito)
        subject_uri = triples_list[0][0]
        
        # Mapear triplos para o formato esperado pela API
        titulo = None
        resumo = None
        tipo_uri = self.default_tipo_uri
        descricao = None
        associatedMedia = []
        temRelacao = []
        
        # Processar cada triplo para extrair informações relevantes
        for s, p, o in triples_list:
            if "title" in p.lower() or "titulo" in p.lower():
                titulo = o
            elif "description" in p.lower() or "descricao" in p.lower() or "resumo" in p.lower():
                if not resumo:  # Usar como resumo se ainda não tiver um
                    resumo = o
                else:  # Caso contrário, usar como descrição detalhada
                    descricao = o
            elif "type" in p.lower() or "tipo" in p.lower():
                tipo_uri = o
            elif "media" in p.lower() or "imagem" in p.lower() or "image" in p.lower():
                associatedMedia.append(o)
            elif "related" in p.lower() or "relacao" in p.lower():
                temRelacao.append(o)
        
        # Garantir que temos pelo menos título e resumo
        if not titulo:
            titulo = "Objeto sem título"
            logger.warning(f"Título não encontrado nos triplos. Usando '{titulo}'.")
        
        if not resumo:
            resumo = "Sem descrição disponível"
            logger.warning(f"Resumo não encontrado nos triplos. Usando '{resumo}'.")
        
        try:
            # Criar o objeto dimensional usando o cliente da API
            result = self.api_client.create_dimensional_object(
                titulo=titulo,
                resumo=resumo,
                tipo_uri=tipo_uri,
                descricao=descricao,
                associatedMedia=associatedMedia if associatedMedia else None,
                temRelacao=temRelacao if temRelacao else None
            )
            
            # Adicionar relações adicionais, se necessário
            if result and "object_uri" in result:
                created_uri = result["object_uri"]
                
                # Adicionar relações que não foram mapeadas diretamente para campos do objeto
                for s, p, o in triples_list:
                    if (p.lower() not in ["title", "titulo", "description", "descricao", "resumo", 
                                         "type", "tipo", "media", "imagem", "image", "related", "relacao"]):
                        try:
                            self.api_client.add_relation(
                                subject_uri=created_uri,
                                predicate_uri=p,
                                object_uri=o
                            )
                        except Exception as e:
                            logger.error(f"Erro ao adicionar relação {p}: {e}")
                
                return result
            else:
                logger.error("Falha ao criar objeto: URI não retornada")
                return {"status": "error", "message": "Falha ao criar objeto: URI não retornada"}
                
        except Exception as e:
            logger.error(f"Erro ao adicionar triplos: {e}")
            return {"status": "error", "message": str(e)}

    def query_triples(self, sparql_query: str) -> Dict[str, Any]:
        """
        Executa uma consulta SPARQL e retorna os resultados.
        Esta funcionalidade não está completamente implementada na API atual.
        
        Args:
            sparql_query: Consulta SPARQL a ser executada
            
        Returns:
            Dict[str, Any]: Resultados da consulta
        """
        logger.warning("Consulta SPARQL direta não implementada na API atual. Use os métodos específicos.")
        
        # Como alternativa, podemos usar o método list_objects para consultas simples
        try:
            return self.api_client.list_objects()
        except Exception as e:
            logger.error(f"Erro ao consultar triplos: {e}")
            return {"status": "error", "message": str(e)}

    def remove_triples(self, triples_list: List[Tuple[str, str, str]]) -> Dict[str, Any]:
        """
        Remove triplos do repositório.
        Esta implementação é simplificada e assume que os triplos estão relacionados a um único objeto.
        
        Args:
            triples_list: Lista de triplos no formato [(sujeito, predicado, objeto), ...]
            
        Returns:
            Dict[str, Any]: Resposta da API
        """
        if not triples_list:
            logger.warning("Lista de triplos vazia. Nada a remover.")
            return {"status": "error", "message": "Lista de triplos vazia"}
        
        # Extrair o URI do sujeito do primeiro triplo (assumindo que todos os triplos têm o mesmo sujeito)
        subject_uri = triples_list[0][0]
        
        try:
            # Excluir o objeto usando o cliente da API
            result = self.api_client.delete_object(subject_uri)
            return result
        except Exception as e:
            logger.error(f"Erro ao remover triplos: {e}")
            return {"status": "error", "message": str(e)}

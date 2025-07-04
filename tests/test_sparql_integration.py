# Módulo de teste para a integração com o backend SPARQL
import os
import sys
import json
import unittest
from unittest.mock import patch, MagicMock

# Adicionar o diretório pai ao sys.path para importar os módulos do projeto
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from storage.rdf_store_interface import RDFStoreInterface
from storage.sparql_api_client import SPARQLAPIClient

class TestSPARQLIntegration(unittest.TestCase):
    """Testes para a integração com o backend SPARQL."""
    
    def setUp(self):
        """Configuração inicial para os testes."""
        self.test_config = {
            "api_base_url": "http://localhost:8000",
            "repository_update_url": "http://localhost:3030/test_dataset/update",
            "repository_base_uri": "http://localhost:3030/test_dataset#",
            "email": "test@example.com",
            "password": "test_password",
            "default_tipo_uri": "http://guara.ueg.br/ontologias/v1/objetos#Documento"
        }
    
    @patch('storage.sparql_api_client.requests.post')
    def test_authentication(self, mock_post):
        """Testa o fluxo de autenticação."""
        # Configurar o mock para simular uma resposta bem-sucedida
        mock_response = MagicMock()
        mock_response.json.return_value = {
            "token": "test_token_123",
            "validade": "2025-06-21T06:50:00Z"
        }
        mock_response.raise_for_status.return_value = None
        mock_post.return_value = mock_response
        
        # Criar o cliente e autenticar
        client = SPARQLAPIClient(
            api_base_url=self.test_config["api_base_url"],
            repository_update_url=self.test_config["repository_update_url"],
            repository_base_uri=self.test_config["repository_base_uri"],
            email=self.test_config["email"],
            password=self.test_config["password"]
        )
        
        # Verificar se a autenticação foi bem-sucedida
        self.assertEqual(client.token, "test_token_123")
        self.assertEqual(client.token_expiry, "2025-06-21T06:50:00Z")
        
        # Verificar se o método post foi chamado com os parâmetros corretos
        mock_post.assert_called_once_with(
            f"{self.test_config['api_base_url']}/acesso/login",
            json={"email": self.test_config["email"], "password": self.test_config["password"]}
        )
    
    @patch('storage.sparql_api_client.requests.post')
    def test_create_dimensional_object(self, mock_post):
        """Testa a criação de um objeto dimensional."""
        # Configurar o mock para simular uma resposta bem-sucedida
        mock_response = MagicMock()
        mock_response.json.return_value = {
            "id": "123e4567-e89b-12d3-a456-426614174000",
            "message": "Objeto dimensional adicionado com sucesso",
            "object_uri": "http://localhost:3030/test_dataset#123e4567-e89b-12d3-a456-426614174000"
        }
        mock_response.raise_for_status.return_value = None
        mock_post.return_value = mock_response
        
        # Criar o cliente e definir o token manualmente
        client = SPARQLAPIClient(
            api_base_url=self.test_config["api_base_url"],
            repository_update_url=self.test_config["repository_update_url"],
            repository_base_uri=self.test_config["repository_base_uri"]
        )
        client.token = "test_token_123"
        
        # Criar um objeto dimensional
        result = client.create_dimensional_object(
            titulo="Manuscrito Antigo",
            resumo="Um manuscrito raro do século XVIII",
            tipo_uri=self.test_config["default_tipo_uri"],
            descricao="Este manuscrito contém informações valiosas sobre a história local."
        )
        
        # Verificar se o resultado é o esperado
        self.assertEqual(result["id"], "123e4567-e89b-12d3-a456-426614174000")
        self.assertEqual(result["object_uri"], "http://localhost:3030/test_dataset#123e4567-e89b-12d3-a456-426614174000")
        
        # Verificar se o método post foi chamado com os parâmetros corretos
        mock_post.assert_called_once()
        args, kwargs = mock_post.call_args
        self.assertEqual(kwargs["headers"]["Authorization"], "Bearer test_token_123")
        self.assertEqual(kwargs["json"]["titulo"], "Manuscrito Antigo")
        self.assertEqual(kwargs["json"]["resumo"], "Um manuscrito raro do século XVIII")
        self.assertEqual(kwargs["json"]["tipo_uri"], self.test_config["default_tipo_uri"])
    
    @patch('storage.sparql_api_client.SPARQLAPIClient.create_dimensional_object')
    def test_rdf_store_interface_add_triples(self, mock_create):
        """Testa a adição de triplos através do RDFStoreInterface."""
        # Configurar o mock para simular uma resposta bem-sucedida
        mock_create.return_value = {
            "id": "123e4567-e89b-12d3-a456-426614174000",
            "message": "Objeto dimensional adicionado com sucesso",
            "object_uri": "http://localhost:3030/test_dataset#123e4567-e89b-12d3-a456-426614174000"
        }
        
        # Criar a interface RDF
        rdf_store = RDFStoreInterface(self.test_config)
        
        # Adicionar triplos
        triples = [
            ("http://example.org/item/123", "http://schema.org/title", "Manuscrito Antigo"),
            ("http://example.org/item/123", "http://schema.org/description", "Um manuscrito raro do século XVIII"),
            ("http://example.org/item/123", "http://www.w3.org/1999/02/22-rdf-syntax-ns#type", "http://guara.ueg.br/ontologias/v1/objetos#Documento")
        ]
        
        result = rdf_store.add_triples(triples)
        
        # Verificar se o resultado é o esperado
        self.assertEqual(result["id"], "123e4567-e89b-12d3-a456-426614174000")
        self.assertEqual(result["object_uri"], "http://localhost:3030/test_dataset#123e4567-e89b-12d3-a456-426614174000")
        
        # Verificar se o método create_dimensional_object foi chamado com os parâmetros corretos
        mock_create.assert_called_once()
        args, kwargs = mock_create.call_args
        self.assertEqual(kwargs["titulo"], "Manuscrito Antigo")
        self.assertEqual(kwargs["resumo"], "Um manuscrito raro do século XVIII")
        self.assertEqual(kwargs["tipo_uri"], "http://guara.ueg.br/ontologias/v1/objetos#Documento")

if __name__ == '__main__':
    unittest.main()

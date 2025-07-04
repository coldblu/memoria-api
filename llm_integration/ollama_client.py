"""
Cliente para integração com Ollama local.

Este módulo fornece uma interface para interagir com modelos de linguagem
através do Ollama executando localmente.
"""
import os
import json
import requests
from typing import Dict, Any, Optional, List, Union

class OllamaClient:
    """
    Cliente para interagir com a API do Ollama local.
    
    Esta classe fornece métodos para gerar texto, embeddings e outras
    funcionalidades usando modelos de linguagem através do Ollama.
    """
    
    def __init__(self, base_url: str = "http://localhost:11434", 
                 model: str = "llama2", 
                 config_path: Optional[str] = None):
        """
        Inicializa o cliente Ollama.
        
        Args:
            base_url: URL base da API Ollama (padrão: http://localhost:11434)
            model: Nome do modelo a ser usado (padrão: llama2)
            config_path: Caminho para arquivo de configuração JSON (opcional)
        """
        self.base_url = base_url
        self.model = model
        self.config = {}
        
        # Carregar configuração do arquivo se fornecido
        if config_path and os.path.exists(config_path):
            try:
                with open(config_path, 'r', encoding='utf-8') as f:
                    self.config = json.load(f)
                    
                # Atualizar configurações a partir do arquivo
                if 'base_url' in self.config:
                    self.base_url = self.config['base_url']
                if 'model' in self.config:
                    self.model = self.config['model']
                    
                print(f"Configuração do Ollama carregada de: {config_path}")
            except Exception as e:
                print(f"Erro ao carregar configuração do Ollama: {e}")
        
        print(f"OllamaClient inicializado. URL: {self.base_url}, Modelo: {self.model}")
    
    def generate_text(self, prompt: str, 
                      system_prompt: Optional[str] = None,
                      temperature: float = 0.7, 
                      max_tokens: int = 500) -> Dict[str, Any]:
        """
        Gera texto a partir de um prompt usando o modelo configurado.
        
        Args:
            prompt: Texto de entrada para o modelo
            system_prompt: Instruções de sistema (opcional)
            temperature: Controle de aleatoriedade (0.0 a 1.0)
            max_tokens: Número máximo de tokens a gerar
            
        Returns:
            Dicionário com a resposta do modelo
        """
        url = f"{self.base_url}/api/generate"
        
        payload = {
            "model": self.model,
            "prompt": prompt,
            "temperature": temperature,
            "max_tokens": max_tokens
        }
        
        if system_prompt:
            payload["system"] = system_prompt
            
        try:
            response = requests.post(url, json=payload)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"Erro na comunicação com Ollama: {e}")
            return {"error": str(e)}
    
    def get_embeddings(self, text: str) -> Dict[str, Any]:
        """
        Obtém embeddings (representações vetoriais) para um texto.
        
        Args:
            text: Texto para gerar embeddings
            
        Returns:
            Dicionário com os embeddings
        """
        url = f"{self.base_url}/api/embeddings"
        
        payload = {
            "model": self.model,
            "prompt": text
        }
        
        try:
            response = requests.post(url, json=payload)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"Erro ao obter embeddings: {e}")
            return {"error": str(e)}
    
    def list_models(self) -> List[str]:
        """
        Lista os modelos disponíveis localmente no Ollama.
        
        Returns:
            Lista de nomes de modelos disponíveis
        """
        url = f"{self.base_url}/api/tags"
        
        try:
            response = requests.get(url)
            response.raise_for_status()
            data = response.json()
            return [model["name"] for model in data.get("models", [])]
        except requests.exceptions.RequestException as e:
            print(f"Erro ao listar modelos: {e}")
            return []
    
    def chat_completion(self, 
                        messages: List[Dict[str, str]], 
                        temperature: float = 0.7,
                        max_tokens: int = 500) -> Dict[str, Any]:
        """
        Realiza uma conversa no formato de chat.
        
        Args:
            messages: Lista de mensagens no formato [{"role": "user", "content": "Olá"}, ...]
            temperature: Controle de aleatoriedade (0.0 a 1.0)
            max_tokens: Número máximo de tokens a gerar
            
        Returns:
            Dicionário com a resposta do modelo
        """
        url = f"{self.base_url}/api/chat"
        
        payload = {
            "model": self.model,
            "messages": messages,
            "temperature": temperature,
            "max_tokens": max_tokens
        }
        
        try:
            response = requests.post(url, json=payload)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"Erro na comunicação com Ollama: {e}")
            return {"error": str(e)}

# Exemplo de uso
if __name__ == "__main__":
    # Criar cliente com configurações padrão
    client = OllamaClient()
    
    # Listar modelos disponíveis
    models = client.list_models()
    print(f"Modelos disponíveis: {models}")
    
    # Gerar texto com um prompt simples
    response = client.generate_text("Explique o que é patrimônio cultural em poucas palavras.")
    if "error" not in response:
        print(f"Resposta: {response.get('response', '')}")
    else:
        print(f"Erro: {response.get('error')}")

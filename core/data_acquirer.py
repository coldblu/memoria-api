# Módulo responsável por aceder a APIs, documentos e outras fontes de dados.
import requests # Para fazer pedidos HTTP a APIs ou páginas web
import os

class DataAcquirer:
    def __init__(self):
        """Inicializa o DataAcquirer."""
        print("DataAcquirer inicializado.")

    def get_data_from_source(self, source_identifier, source_type="url"):
        """
        Obtém dados de diferentes fontes.

        Args:
            source_identifier (str): O identificador da fonte (ex: URL, caminho do ficheiro).
            source_type (str): O tipo de fonte. Suportado: "url", "local_file_txt".

        Returns:
            dict or None: Um dicionário com os dados extraídos (ex: {"content": "..."}) 
                          ou None se a obtenção falhar ou o tipo não for suportado.
        """
        print(f"A adquirir dados de '{source_identifier}' (tipo: {source_type})")
        data = None

        if source_type == "url":
            try:
                response = requests.get(source_identifier, timeout=10)
                response.raise_for_status() # Levanta um erro para códigos de status HTTP 4xx/5xx
                # Tenta obter JSON, se falhar, obtém texto
                try:
                    data = {"content_json": response.json()}
                    print(f"Dados JSON obtidos de URL: {source_identifier}")
                except requests.exceptions.JSONDecodeError:
                    data = {"content_text": response.text}
                    print(f"Dados de texto obtidos de URL: {source_identifier}")
            except requests.exceptions.RequestException as e:
                print(f"Erro ao aceder à URL {source_identifier}: {e}")
                return None

        elif source_type == "local_file_txt":
            try:
                if not os.path.exists(source_identifier):
                    print(f"Erro: Ficheiro local não encontrado em {source_identifier}")
                    return None
                with open(source_identifier, 'r', encoding='utf-8') as f:
                    data = {"content_text": f.read()}
                print(f"Dados de texto obtidos do ficheiro local: {source_identifier}")
            except Exception as e:
                print(f"Erro ao ler o ficheiro local {source_identifier}: {e}")
                return None
        
        # Futuramente, adicionar suporte para outros tipos como "local_file_pdf", "api_specific_call"
        # Para PDF, poderia usar bibliotecas como PyPDF2 ou pdfminer.six
        # Para APIs específicas, poderia ter lógica para construir pedidos mais complexos.

        else:
            print(f"Tipo de fonte '{source_type}' não suportado.")
            return None

        return data

if __name__ == '__main__':
    acquirer = DataAcquirer()

    # Teste com URL (JSON placeholder)
    json_url = "https://jsonplaceholder.typicode.com/todos/1"
    print(f"\nA testar obtenção de dados de URL (JSON): {json_url}")
    json_data = acquirer.get_data_from_source(json_url, source_type="url")
    if json_data:
        print("Dados obtidos (JSON):")
        # print(json_data.get("content_json"))
    else:
        print("Falha ao obter dados JSON.")

    # Teste com URL (HTML/texto)
    html_url = "http://example.com"
    print(f"\nA testar obtenção de dados de URL (HTML/Texto): {html_url}")
    html_data = acquirer.get_data_from_source(html_url, source_type="url")
    if html_data:
        print("Dados obtidos (HTML/Texto) - primeiros 100 caracteres:")
        # print(html_data.get("content_text", "")[:100] + "...")
    else:
        print("Falha ao obter dados HTML/Texto.")

    # Teste com ficheiro local (criar um ficheiro de teste primeiro)
    test_file_path = "/home/ubuntu/agente_catalogador_ia/storage/test_document.txt"
    print(f"\nA testar obtenção de dados de ficheiro local: {test_file_path}")
    os.makedirs(os.path.dirname(test_file_path), exist_ok=True)
    with open(test_file_path, 'w', encoding='utf-8') as f_test:
        f_test.write("Este é um documento de teste para o DataAcquirer.\nContém múltiplas linhas de texto.")
    
    file_data = acquirer.get_data_from_source(test_file_path, source_type="local_file_txt")
    if file_data:
        print("Dados obtidos do ficheiro:")
        # print(file_data.get("content_text"))
    else:
        print("Falha ao obter dados do ficheiro.")

    # Teste com tipo não suportado
    print(f"\nA testar tipo de fonte não suportado:")
    invalid_data = acquirer.get_data_from_source("some_identifier", source_type="invalid_type")
    if not invalid_data:
        print("Teste de tipo inválido passou como esperado.")


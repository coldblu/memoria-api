# Módulo para buscar referências e adicionar URIs.
import json

class ReferenceLinker:
    def __init__(self, db_connector=None, rdf_store=None):
        """
        Inicializa o ReferenceLinker.
        Pode usar um conector de base de dados tradicional (db_connector)
        ou um repositório RDF (rdf_store) para verificar/adicionar URIs.
        """
        self.db_connector = db_connector
        self.rdf_store = rdf_store
        print("ReferenceLinker inicializado.")

    def find_and_link_references(self, item_data, existing_uris_file="/home/ubuntu/agente_catalogador_ia/storage/known_uris.json"):
        """
        Lógica para buscar referências na base de dados do utilizador e na web (simulado).
        Adiciona URIs encontradas a um ficheiro JSON para simulação.

        Args:
            item_data (dict): Dados do item para o qual procurar referências.
            existing_uris_file (str): Caminho para um ficheiro JSON que armazena URIs conhecidas (simulação).

        Returns:
            list: Lista de URIs encontradas e adicionadas/confirmadas.
        """
        print(f"A procurar referências para: {item_data.get('title', 'Título Desconhecido')}")
        found_uris = []

        # Simulação de busca em base de dados interna
        if self.db_connector:
            # Supondo que item_data tem um 'id_interno'
            # query_result = self.db_connector.execute_query(f"SELECT uri FROM references WHERE item_id = {item_data.get('id_interno')}")
            # if query_result:
            #     found_uris.extend(query_result)
            print("Simulando busca em base de dados interna...")
            # Exemplo: se o item tiver 'autor' na base de dados, adiciona uma URI de autor fictícia
            if "autor" in item_data:
                autor_uri = f"http://example.org/autor/{item_data['autor'].replace(' ', '_')}"
                found_uris.append(autor_uri)
                print(f"URI de autor interno encontrada/gerada: {autor_uri}")

        # Simulação de busca na web
        print("Simulando busca de referências na web...")
        if "title" in item_data:
            web_reference_uri = f"http://example-search.com/results?query={item_data['title'].replace(' ', '+')}"
            found_uris.append(web_reference_uri)
            print(f"URI de referência web encontrada/gerada: {web_reference_uri}")

        # Adicionar/confirmar URIs num ficheiro JSON (simulação de persistência)
        try:
            with open(existing_uris_file, 'r+') as f:
                try:
                    known_uris = json.load(f)
                except json.JSONDecodeError:
                    known_uris = [] # Ficheiro existe mas está vazio ou corrompido
                
                for uri in found_uris:
                    if uri not in known_uris:
                        known_uris.append(uri)
                
                f.seek(0)
                json.dump(known_uris, f, indent=4)
                f.truncate()
            print(f"URIs atualizadas em {existing_uris_file}")
        except FileNotFoundError:
            with open(existing_uris_file, 'w') as f:
                json.dump(found_uris, f, indent=4)
            print(f"Ficheiro de URIs criado: {existing_uris_file} com {len(found_uris)} URIs.")
        except Exception as e:
            print(f"Erro ao guardar URIs no ficheiro {existing_uris_file}: {e}")

        item_data['linked_uris'] = found_uris # Adiciona as URIs encontradas aos dados do item
        return found_uris

if __name__ == '__main__':
    # Exemplo de uso (para teste)
    linker = ReferenceLinker()
    test_item = {"title": "A Arte da Guerra", "autor": "Sun Tzu"}
    uris = linker.find_and_link_references(test_item)
    print(f"URIs ligadas ao item: {uris}")
    print(f"Dados do item atualizados: {test_item}")

    test_item_2 = {"title": "O Príncipe", "id_interno": 123}
    uris_2 = linker.find_and_link_references(test_item_2)
    print(f"URIs ligadas ao item 2: {uris_2}")


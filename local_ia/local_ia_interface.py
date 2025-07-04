# Interface para carregar e utilizar os modelos de IA locais.
import os
# Importar a classe base para garantir a mesma interface que os clientes externos
from agente_catalogador_ia.apis.external_ia_clients import BaseIAClient

class LocalIAInterface(BaseIAClient):
    """Interface para carregar e utilizar os modelos de IA locais."""
    def __init__(self, model_path=None, model_name="local_default_model"):
        """
        Inicializa a interface de IA Local.

        Args:
            model_path (str, optional): Caminho para o diretório ou ficheiro do modelo local.
                                        Pode ser configurado via variável de ambiente LOCAL_IA_MODEL_PATH.
            model_name (str, optional): Nome do modelo local a ser carregado.
        """
        super().__init__(model_name=model_name) # Não necessita de API key
        self.model_path = model_path or os.getenv("LOCAL_IA_MODEL_PATH", "/home/ubuntu/agente_catalogador_ia/local_ia/models/default_model_placeholder")
        self.model = None
        self._load_model()

    def _load_model(self):
        """Lógica para carregar o modelo de IA local (simulado)."""
        print(f"A tentar carregar modelo de IA local: {self.model_name} de {self.model_path}")
        # Simulação de carregamento de modelo.
        # Numa implementação real, usaria bibliotecas como TensorFlow, PyTorch, Hugging Face Transformers, etc.
        if os.path.exists(self.model_path) or "placeholder" in self.model_path: # Aceita placeholder para teste
            self.model = f"ModeloLocalSimulado::{self.model_name}@{self.model_path}"
            print(f"Modelo local \'{self.model_name}\' carregado (simulado) de: {self.model_path}")
        else:
            print(f"Aviso: Caminho do modelo local não encontrado: {self.model_path}. O modelo local não será funcional.")
            self.model = None

    def generate_text(self, prompt, max_tokens=150):
        """Gera texto com base num prompt usando o modelo local (simulado)."""
        if not self.model:
            return f"[Modelo Local não carregado. Não é possível processar: {prompt[:50]}...]"
        print(f"Modelo local ({self.model_name}) a gerar texto para: {prompt[:50]}...")
        # Simulação de geração de texto
        return f"[Texto gerado pelo Modelo Local ({self.model_name}) para o prompt: {prompt}] (max_tokens: {max_tokens})"

    def analyze_text(self, text, analysis_type="sentiment"):
        """Analisa texto usando o modelo local (simulado)."""
        if not self.model:
            return f"[Modelo Local não carregado. Não é possível analisar: {text[:50]}...]"
        print(f"Modelo local ({self.model_name}) a analisar texto ({analysis_type}): {text[:50]}...")
        # Simulação de análise de texto
        return f"[Análise ({analysis_type}) pelo Modelo Local ({self.model_name}): {text[:100]}... - Resultado Simulado]"

if __name__ == '__main__':
    print("Testando Local IA Interface...")
    # Criar um diretório e ficheiro de modelo placeholder se não existir
    placeholder_path = "/home/ubuntu/agente_catalogador_ia/local_ia/models/default_model_placeholder"
    os.makedirs(os.path.dirname(placeholder_path), exist_ok=True)
    if not os.path.exists(placeholder_path):
        with open(placeholder_path, "w") as f:
            f.write("Este é um ficheiro de modelo placeholder.")

    local_ia = LocalIAInterface()
    if local_ia.model:
        print("\n--- Teste Geração de Texto Local ---")
        prompt_local = "Descreve um artefacto antigo."
        resposta_local = local_ia.generate_text(prompt_local)
        print(f"Prompt Local: {prompt_local}")
        print(f"Resposta Local: {resposta_local}")

        print("\n--- Teste Análise de Texto Local ---")
        texto_analise = "Este artefacto é incrivelmente belo e bem preservado."
        analise_local = local_ia.analyze_text(texto_analise, analysis_type="emotion")
        print(f"Texto para Análise: {texto_analise}")
        print(f"Resultado da Análise Local: {analise_local}")
    else:
        print("Modelo local não foi carregado. Testes não podem ser executados.")

    print("\nTestando com caminho de modelo inválido:")
    local_ia_invalido = LocalIAInterface(model_path="/caminho/invalido/modelo")
    if not local_ia_invalido.model:
        print("Teste com caminho inválido comportou-se como esperado (modelo não carregado).")


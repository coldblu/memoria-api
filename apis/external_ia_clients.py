# Clientes para interagir com APIs de IA externas (ex: OpenAI, Google Gemini).
import requests
import os

class BaseIAClient:
    """Classe base para clientes de IA."""
    def __init__(self, api_key=None, model_name=None):
        self.api_key = api_key or os.getenv("DEFAULT_IA_API_KEY")
        self.model_name = model_name
        if not self.api_key and not isinstance(self, LocalIAInterface): # LocalIAInterface não precisa de API key
            print(f"Aviso: API Key não fornecida para {self.__class__.__name__} e DEFAULT_IA_API_KEY não definida.")

    def generate_text(self, prompt, max_tokens=150):
        """Gera texto com base num prompt."""
        raise NotImplementedError("Este método deve ser implementado pela subclasse.")

    def analyze_text(self, text, analysis_type="sentiment"):
        """Analisa texto para um determinado tipo de análise."""
        raise NotImplementedError("Este método deve ser implementado pela subclasse.")

class OpenAIAClient(BaseIAClient):
    """Cliente para a API da OpenAI."""
    def __init__(self, api_key=None, model_name="text-davinci-003"):
        super().__init__(api_key=api_key or os.getenv("OPENAI_API_KEY"), model_name=model_name)
        self.api_url = "https://api.openai.com/v1/completions" # Exemplo, pode variar
        if not self.api_key:
            print("Aviso: OpenAI API Key não configurada. As chamadas à OpenAI falharão.")

    def generate_text(self, prompt, max_tokens=150):
        if not self.api_key:
            print("Falha na geração de texto: OpenAI API Key em falta.")
            return f"[Simulação OpenAI: {prompt[:50]}...]"
        
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        data = {
            "model": self.model_name,
            "prompt": prompt,
            "max_tokens": max_tokens
        }
        try:
            response = requests.post(self.api_url, headers=headers, json=data, timeout=20)
            response.raise_for_status()
            return response.json()["choices"][0]["text"].strip()
        except requests.exceptions.RequestException as e:
            print(f"Erro ao chamar a API da OpenAI: {e}")
            return f"[Erro na simulação OpenAI ao processar: {prompt[:50]}...]"
        except KeyError:
            print(f"Erro ao processar resposta da OpenAI: {response.text}")
            return f"[Erro na simulação OpenAI - resposta inesperada]"

class GeminiAPIClient(BaseIAClient):
    """Cliente para a API do Google Gemini (Exemplo)."""
    def __init__(self, api_key=None, model_name="gemini-pro"):
        super().__init__(api_key=api_key or os.getenv("GEMINI_API_KEY"), model_name=model_name)
        # self.api_url = "URL_DA_API_GEMINI" # Substituir pela URL correta
        if not self.api_key:
            print("Aviso: Gemini API Key não configurada. As chamadas ao Gemini falharão.")

    def generate_text(self, prompt, max_tokens=150):
        if not self.api_key:
            print("Falha na geração de texto: Gemini API Key em falta.")
            return f"[Simulação Gemini: {prompt[:50]}...]"
        # Lógica de chamada à API do Gemini (simulada)
        print(f"A chamar API Gemini (simulado) para: {prompt[:50]}... com modelo {self.model_name}")
        return f"Texto gerado pela API Gemini (simulado) para o prompt: {prompt}"

# Importar LocalIAInterface para evitar dependência circular se for movido para outro ficheiro
# from agente_catalogador_ia.local_ia.local_ia_interface import LocalIAInterface
# Esta linha será comentada pois LocalIAInterface está noutro ficheiro e será gerida pelo IAManager

if __name__ == '__main__':
    print("Testando External IA Clients...")
    # Para testar, defina as variáveis de ambiente OPENAI_API_KEY ou GEMINI_API_KEY
    # ou passe as chaves diretamente no construtor.

    # Teste OpenAI (requer chave de API válida como variável de ambiente ou no construtor)
    # openai_client = OpenAIAClient(api_key="SUA_CHAVE_OPENAI_AQUI_SE_NAO_ESTIVER_NO_AMBIENTE")
    openai_client = OpenAIAClient()
    if openai_client.api_key:
        print("\n--- Teste OpenAI ---")
        prompt_openai = "Escreve um poema curto sobre a lua."
        resposta_openai = openai_client.generate_text(prompt_openai)
        print(f"Prompt OpenAI: {prompt_openai}")
        print(f"Resposta OpenAI: {resposta_openai}")
    else:
        print("\n--- Teste OpenAI (API Key em falta) ---")
        prompt_openai = "Escreve um poema curto sobre a lua."
        resposta_openai = openai_client.generate_text(prompt_openai)
        print(f"Prompt OpenAI: {prompt_openai}")
        print(f"Resposta OpenAI (simulada): {resposta_openai}")


    # Teste Gemini (simulado, não requer chave real para este exemplo)
    gemini_client = GeminiAPIClient()
    print("\n--- Teste Gemini (Simulado) ---")
    prompt_gemini = "Qual é a capital de Portugal?"
    resposta_gemini = gemini_client.generate_text(prompt_gemini)
    print(f"Prompt Gemini: {prompt_gemini}")
    print(f"Resposta Gemini: {resposta_gemini}")


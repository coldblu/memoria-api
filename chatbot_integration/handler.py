# Módulo para processar os pedidos do chatbot e formular respostas.

class ChatbotHandler:
    def __init__(self, agent_instance):
        self.agent = agent_instance
        pass

    def handle_message(self, user_message):
        # Lógica para interpretar a mensagem do utilizador
        # Chamar o self.agent.process_request() com os dados apropriados
        # Formular uma resposta para o chatbot
        response = self.agent.process_request({"query": user_message, "source": "chatbot"})
        return f"Resposta do Agente: {response}"


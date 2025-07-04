# check_env.py
import os

# Tenta ler a variável de ambiente GEMINI_API_KEY
api_key = os.getenv("GEMINI_API_KEY")

print("-" * 50)
if api_key:
    print("✅ SUCESSO! A variável de ambiente GEMINI_API_KEY foi encontrada.")
    # Mostra apenas os primeiros e últimos caracteres por segurança
    print(f"   Valor: {api_key[:4]}...{api_key[-4:]}")
else:
    print("❌ FALHA! A variável de ambiente GEMINI_API_KEY não foi encontrada.")
    print("   Por favor, certifique-se de que a definiu no mesmo terminal antes de executar o servidor.")
print("-" * 50)

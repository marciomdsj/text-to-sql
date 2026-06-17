import ollama

# Teste simples: pergunta algo ao modelo
resposta = ollama.chat(
    model='qwen2.5-coder:7b',
    messages=[
        {
            'role': 'user',
            'content': 'Escreva uma query SQL que retorne o nome de todos os clientes.'
        }
    ]
)

print(resposta['message']['content'])    
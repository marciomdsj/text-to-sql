import mysql.connector
import psycopg2
import ollama
import time

# ============================
# CONFIGURAÇÃO
# ============================
BANCO = 'postgres'  # 'mysql' ou 'postgres'
MODELO = 'qwen2.5-coder:7b'

# ============================
# CONEXÕES
# ============================
def conectar_mysql():
    return mysql.connector.connect(
        host='127.0.0.1',
        user='root',
        password='root',
        database='Chinook',
        unix_socket='/tmp/mysql.sock'
    )

def conectar_postgres():
    return psycopg2.connect(
        host='localhost',
        user='marciomdsj',
        password='',
        database='chinook',
        port=5432
    )

# ============================
# SCHEMA
# ============================
def pegar_schema_mysql(cursor):
    cursor.execute("SHOW TABLES;")
    tabelas = cursor.fetchall()
    schema_str = ""
    for t in tabelas:
        nome = t[0]
        cursor.execute(f"DESCRIBE {nome};")
        colunas = cursor.fetchall()
        schema_str += f"\nTabela {nome}:\n"
        for col in colunas:
            schema_str += f"  - {col[0]} ({col[1]})\n"
    return schema_str

def pegar_schema_postgres(cursor):
    cursor.execute("""
        SELECT table_name FROM information_schema.tables 
        WHERE table_schema = 'public' 
        ORDER BY table_name;
    """)
    tabelas = cursor.fetchall()
    schema_str = ""
    for t in tabelas:
        nome = t[0]
        cursor.execute(f"""
            SELECT column_name, data_type 
            FROM information_schema.columns 
            WHERE table_name = '{nome}' AND table_schema = 'public'
            ORDER BY ordinal_position;
        """)
        colunas = cursor.fetchall()
        schema_str += f"\nTabela {nome}:\n"
        for col in colunas:
            schema_str += f"  - {col[0]} ({col[1]})\n"
    return schema_str

# ============================
# TEXT-TO-SQL
# ============================
def texto_para_sql(pergunta, schema, banco):
    prompt = f"""Você é um especialista em SQL para {banco.upper()}. Sua tarefa é converter perguntas em linguagem natural para queries SQL válidas.

REGRAS IMPORTANTES:
1. Use EXATAMENTE os nomes de tabelas e colunas conforme o schema abaixo
2. Retorne APENAS a query SQL, sem markdown, sem ```sql, sem explicações
3. Use JOINs explícitos quando necessário

Schema do banco:
{schema}

Pergunta do usuário: {pergunta}

Query SQL:"""

    resposta = ollama.chat(
        model=MODELO,
        messages=[{'role': 'user', 'content': prompt}]
    )
    sql = resposta['message']['content'].strip()
    sql = sql.replace('```sql', '').replace('```', '').strip()
    return sql

# ============================
# EXECUÇÃO PRINCIPAL
# ============================
if BANCO == 'mysql':
    conn = conectar_mysql()
    cursor = conn.cursor()
    schema = pegar_schema_mysql(cursor)
elif BANCO == 'postgres':
    conn = conectar_postgres()
    cursor = conn.cursor()
    schema = pegar_schema_postgres(cursor)

pergunta = "Quais são os 5 artistas com mais faixas? Mostre o nome do artista e quantas faixas."

print(f"Banco: {BANCO.upper()}")
print(f"Pergunta: {pergunta}\n")

inicio = time.time()
sql_gerado = texto_para_sql(pergunta, schema, BANCO)
tempo_llm = time.time() - inicio
print(f"SQL gerado em {tempo_llm:.2f}s:\n{sql_gerado}\n")

inicio = time.time()
cursor.execute(sql_gerado)
resultado = cursor.fetchall()
tempo_sql = time.time() - inicio
print(f"Executado em {tempo_sql:.2f}s")
print(f"Resultado: {resultado}")

cursor.close()
conn.close()
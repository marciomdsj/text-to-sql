"""
Text-to-SQL com Ollama
Interface Streamlit para consultas em linguagem natural
"""

import os
import streamlit as st
import mysql.connector
import psycopg2
import ollama
import pandas as pd
import time
from dotenv import load_dotenv


load_dotenv()


# CONFIGURAÇÃO DA PÁGINA

st.set_page_config(
    page_title="Text-to-SQL",
    page_icon="🎵",
    layout="wide"
)


# FUNÇÕES DE CONEXÃO

def conectar_mysql(database):
    return mysql.connector.connect(
        host=os.getenv('MYSQL_HOST', '127.0.0.1'),
        user=os.getenv('MYSQL_USER', 'root'),
        password=os.getenv('MYSQL_PASSWORD', ''),
        database=database,
        unix_socket=os.getenv('MYSQL_SOCKET', '/tmp/mysql.sock')
    )

def conectar_postgres(database):
    return psycopg2.connect(
        host=os.getenv('POSTGRES_HOST', 'localhost'),
        user=os.getenv('POSTGRES_USER', ''),
        password=os.getenv('POSTGRES_PASSWORD', ''),
        database=database,
        port=int(os.getenv('POSTGRES_PORT', 5432))
    )


# FUNÇÕES DE SCHEMA

def pegar_schema_mysql(cursor):
    cursor.execute("SHOW TABLES;")
    tabelas = cursor.fetchall()
    schema = {}
    for t in tabelas:
        nome = t[0]
        cursor.execute(f"DESCRIBE {nome};")
        colunas = cursor.fetchall()
        schema[nome] = [(col[0], col[1]) for col in colunas]
    return schema

def pegar_schema_postgres(cursor):
    cursor.execute("""
        SELECT table_name FROM information_schema.tables 
        WHERE table_schema = 'public' 
        ORDER BY table_name;
    """)
    tabelas = cursor.fetchall()
    schema = {}
    for t in tabelas:
        nome = t[0]
        cursor.execute(f"""
            SELECT column_name, data_type 
            FROM information_schema.columns 
            WHERE table_name = '{nome}' AND table_schema = 'public'
            ORDER BY ordinal_position;
        """)
        colunas = cursor.fetchall()
        schema[nome] = [(col[0], col[1]) for col in colunas]
    return schema

def schema_para_string(schema):
    """Converte o dict do schema em string para o prompt"""
    s = ""
    for tabela, colunas in schema.items():
        s += f"\nTabela {tabela}:\n"
        for col_nome, col_tipo in colunas:
            s += f"  - {col_nome} ({col_tipo})\n"
    return s


# TEXT-TO-SQL

def texto_para_sql(pergunta, schema_str, banco, modelo):
    prompt = f"""Você é um especialista em SQL para {banco.upper()}. Sua tarefa é converter perguntas em linguagem natural para queries SQL válidas.

REGRAS IMPORTANTES:
1. Use EXATAMENTE os nomes de tabelas e colunas conforme o schema abaixo
2. Retorne APENAS a query SQL, sem markdown, sem ```sql, sem explicações
3. Use JOINs explícitos quando necessário

Schema do banco:
{schema_str}

Pergunta do usuário: {pergunta}

Query SQL:"""

    resposta = ollama.chat(
        model=modelo,
        messages=[{'role': 'user', 'content': prompt}]
    )
    sql = resposta['message']['content'].strip()
    sql = sql.replace('```sql', '').replace('```', '').strip()
    return sql


# INTERFACE

st.title("🔍 Text-to-SQL com Ollama")
st.caption("Consulte bancos de dados em linguagem natural")

# Sidebar — Configurações

with st.sidebar:
    st.header("⚙️ Configurações")
    
    banco = st.selectbox(
        "Banco de Dados",
        options=['MySQL', 'PostgreSQL'],
        index=0
    )

    # Datasets disponíveis com nomes de database por servidor
    DATASETS = {
        'Chinook': {'MySQL': 'Chinook', 'PostgreSQL': 'chinook'},
        'Netflix': {'MySQL': 'netflixdb', 'PostgreSQL': 'netflixdb'},
        'Outro (digitar)': None,
    }

    dataset = st.selectbox("Dataset", options=list(DATASETS.keys()), index=0)

    if DATASETS[dataset] is not None:
        database_nome = DATASETS[dataset][banco]
        st.caption(f"Database: `{database_nome}`")
    else:
        database_nome = st.text_input("Nome do database")
    
    modelo = st.selectbox(
        "Modelo LLM",
        options=['qwen2.5-coder:7b', 'qwen2.5-coder:3b', 'llama3.2:3b', 'gemma3:4b'],
        index=0
    )
    
    st.divider()
    
    # Tenta carregar schema

    schema_dict = None
    try:
        if banco == 'MySQL':
            conn = conectar_mysql(database_nome)
            cursor = conn.cursor()
            schema_dict = pegar_schema_mysql(cursor)
        else:
            conn = conectar_postgres(database_nome)
            cursor = conn.cursor()
            schema_dict = pegar_schema_postgres(cursor)
        
        cursor.close()
        conn.close()
        
        st.success(f"✅ Conectado em {banco}")
        
        # Mostrar schema

        with st.expander("📋 Ver schema completo", expanded=False):
            for tabela, colunas in schema_dict.items():
                st.markdown(f"**{tabela}**")
                for col_nome, col_tipo in colunas:
                    st.text(f"  • {col_nome} ({col_tipo})")
    
    except Exception as e:
        st.error(f"❌ Erro de conexão: {str(e)}")

# Área principal

if schema_dict:
    pergunta = st.text_area(
        "💬 Sua pergunta em linguagem natural:",
        placeholder="Ex: Quais são os 5 artistas com mais faixas?",
        height=100
    )
    
    if st.button("🔍 Gerar SQL e Buscar", type="primary"):
        if not pergunta.strip():
            st.warning("Digite uma pergunta primeiro.")
        else:
            schema_str = schema_para_string(schema_dict)
            
            # Gerar SQL
            
            with st.spinner("🤖 LLM gerando SQL..."):
                inicio = time.time()
                try:
                    sql_gerado = texto_para_sql(pergunta, schema_str, banco, modelo)
                    tempo_llm = time.time() - inicio
                    
                    st.subheader("📝 SQL Gerado")
                    st.code(sql_gerado, language='sql')
                    st.caption(f"⏱️ Tempo do LLM: {tempo_llm:.2f}s")
                    
                except Exception as e:
                    st.error(f"Erro ao gerar SQL: {str(e)}")
                    st.stop()
            
            # Executar SQL

            with st.spinner("🗄️ Executando no banco..."):
                inicio = time.time()
                try:
                    if banco == 'MySQL':
                        conn = conectar_mysql(database_nome)
                    else:
                        conn = conectar_postgres(database_nome)
                    
                    cursor = conn.cursor()
                    cursor.execute(sql_gerado)
                    resultado = cursor.fetchall()
                    colunas = [desc[0] for desc in cursor.description]
                    tempo_sql = time.time() - inicio
                    
                    cursor.close()
                    conn.close()
                    
                    st.subheader("📊 Resultado")
                    st.caption(f"⏱️ Tempo do SQL: {tempo_sql:.2f}s | 📈 {len(resultado)} linha(s)")
                    
                    if resultado:
                        df = pd.DataFrame(resultado, columns=colunas)
                        st.dataframe(df, use_container_width=True)
                    else:
                        st.info("A query não retornou resultados.")
                
                except Exception as e:
                    st.error(f"Erro ao executar SQL: {str(e)}")
                    st.info("💡 Dica: tente reformular a pergunta ou usar o modelo 7b para melhor precisão.")

else:
    st.info("👈 Configure a conexão na barra lateral para começar.")
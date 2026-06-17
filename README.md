# Text-to-SQL com Ollama

Ferramenta que converte perguntas em linguagem natural para consultas SQL, usando LLMs locais via Ollama.
Desenvolvida como trabalho final da disciplina ICSB30 - Introdução a Banco de Dados.

## Como funciona

1. A aplicação se conecta a um banco de dados (MySQL ou PostgreSQL)
2. Carrega automaticamente o schema (tabelas e colunas)
3. O usuário digita uma pergunta em linguagem natural
4. Um modelo LLM local (via Ollama) converte a pergunta em SQL
5. A query é executada no banco e os resultados são exibidos em tela

## Pré-requisitos

- Python 3.10+
- MySQL e/ou PostgreSQL instalado e rodando
- [Ollama](https://ollama.com/) instalado

## Instalação

### 1. Clonar o repositório

```bash
git clone <url-do-repositorio>
cd text-to-sql
```

### 2. Criar ambiente virtual e instalar dependências

```bash
python3 -m venv venv
source venv/bin/activate   # Linux/macOS
# venv\Scripts\activate    # Windows
pip install -r requirements.txt
```

### 3. Baixar o modelo LLM no Ollama

```bash
ollama pull qwen2.5-coder:7b
```

Outros modelos suportados: `qwen2.5-coder:3b`, `llama3.2:3b`, `gemma3:4b`.

### 4. Importar os bancos de dados

O projeto inclui dois datasets: **Chinook** (catálogo de música) e **Netflix** (filmes e séries).
Importe um ou ambos, conforme o servidor que estiver usando.

> O script do Chinook já cria o banco automaticamente.
> O script do Netflix **não** cria — é preciso criar o banco antes de importar.

**MySQL:**
```bash
mysql -u root -p < Chinook_MySql.sql

mysql -u root -p -e "CREATE DATABASE IF NOT EXISTS netflixdb;"
mysql -u root -p netflixdb < Netflix_MySql.sql
```

**PostgreSQL:**
```bash
createdb chinook
psql chinook < Chinook_PostgreSql.sql

createdb netflixdb
psql netflixdb < Netflix_PostgreSql.sql
```

### 5. Configurar variáveis de ambiente

Copie o arquivo de exemplo e edite com suas credenciais:

```bash
cp .env.example .env
```

Edite o `.env` com seus dados de conexão (host, usuário, senha, etc.).

### 6. Rodar a aplicação

```bash
streamlit run app.py
```

A interface abrirá automaticamente no navegador (http://localhost:8501).

## Uso

1. Na barra lateral, selecione o banco de dados (MySQL ou PostgreSQL)
2. Escolha o dataset (Chinook, Netflix ou digite o nome de outro database)
3. Selecione o modelo LLM
3. Se a conexão for bem-sucedida, o schema será exibido na sidebar
4. Digite sua pergunta em linguagem natural na área de texto
5. Clique em "Gerar SQL e Buscar"
6. O SQL gerado e os resultados serão exibidos na tela

### Exemplos de perguntas (Chinook)

- "Quais são os 5 artistas com mais faixas?"
- "Quantas músicas tem o gênero Rock?"
- "Liste os 10 clientes que mais gastaram, com nome e total"
- "Quais álbuns foram lançados pelo artista AC/DC?"

### Exemplos de perguntas (Netflix)

- "Quais são os 10 filmes mais assistidos?"
- "Quantos filmes em português existem no catálogo?"
- "Quais séries têm mais temporadas?"
- "Liste os filmes lançados em 2024 com mais horas assistidas"

## Estrutura do projeto

```
text-to-sql/
├── app.py                  # Aplicação principal (Streamlit)
├── requirements.txt        # Dependências Python
├── .env.example            # Template de variáveis de ambiente
├── .gitignore              # Arquivos ignorados pelo Git
├── Chinook_MySql.sql       # Script de criação do banco Chinook (MySQL)
├── Chinook_PostgreSql.sql  # Script de criação do banco Chinook (PostgreSQL)
├── Netflix_MySql.sql       # Script de criação do banco Netflix (MySQL)
├── Netflix_PostgreSql.sql  # Script de criação do banco Netflix (PostgreSQL)
└── tests/                  # Scripts de teste
    ├── teste_mysql.py      # Teste de conexão MySQL
    ├── teste_postgres.py   # Teste de conexão PostgreSQL
    ├── teste_ollama.py     # Teste do modelo LLM
    └── teste_text_to_sql.py # Teste do fluxo completo (terminal)
```

## Tecnologias

- **Python** — linguagem principal
- **Streamlit** — interface web
- **Ollama** — servidor local de LLMs
- **mysql-connector-python** — driver MySQL
- **psycopg2** — driver PostgreSQL
- **pandas** — exibição de resultados em tabela
- **python-dotenv** — carregamento de variáveis de ambiente

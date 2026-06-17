import os
import mysql.connector
from dotenv import load_dotenv

load_dotenv()

conn = mysql.connector.connect(
    host=os.getenv('MYSQL_HOST', '127.0.0.1'),
    user=os.getenv('MYSQL_USER', 'root'),
    password=os.getenv('MYSQL_PASSWORD', ''),
    database=os.getenv('MYSQL_DATABASE', 'Chinook'),
    unix_socket=os.getenv('MYSQL_SOCKET', '/tmp/mysql.sock')
)

cursor = conn.cursor()

# Listar todas as tabelas
cursor.execute("SHOW TABLES;")
tabelas = cursor.fetchall()

print(f"Tabelas no banco {os.getenv('MYSQL_DATABASE', 'Chinook')}:")
for t in tabelas:
    print(f"  - {t[0]}")

# Para cada tabela, listar as colunas
print("\nDetalhes das tabelas:")
for t in tabelas:
    nome_tabela = t[0]
    cursor.execute(f"DESCRIBE {nome_tabela};")
    colunas = cursor.fetchall()
    print(f"\n{nome_tabela}:")
    for col in colunas:
        print(f"  {col[0]} ({col[1]})")

cursor.close()
conn.close()

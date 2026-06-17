import mysql.connector

# Conexão com MySQL
conn = mysql.connector.connect(
    host='127.0.0.1',
    user='root',
    password='root',
    database='tpch',
    unix_socket='/tmp/mysql.sock'
)

cursor = conn.cursor()

# Listar todas as tabelas
cursor.execute("SHOW TABLES;")
tabelas = cursor.fetchall()

print("Tabelas no banco tpch:")
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
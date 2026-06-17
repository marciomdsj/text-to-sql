import os
import psycopg2
from dotenv import load_dotenv

load_dotenv()

conn = psycopg2.connect(
    host=os.getenv('POSTGRES_HOST', 'localhost'),
    user=os.getenv('POSTGRES_USER', ''),
    password=os.getenv('POSTGRES_PASSWORD', ''),
    database=os.getenv('POSTGRES_DATABASE', 'chinook'),
    port=int(os.getenv('POSTGRES_PORT', 5432))
)

cursor = conn.cursor()

# Listar tabelas
cursor.execute("""
    SELECT table_name FROM information_schema.tables
    WHERE table_schema = 'public'
    ORDER BY table_name;
""")
tabelas = cursor.fetchall()
print("Tabelas:")
for t in tabelas:
    print(f"  - {t[0]}")

# Testar uma query
cursor.execute("SELECT name FROM artist LIMIT 5;")
print("\nPrimeiros 5 artistas:")
for row in cursor.fetchall():
    print(f"  - {row[0]}")

cursor.close()
conn.close()

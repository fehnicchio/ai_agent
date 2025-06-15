# test_db.py
import psycopg2
import os
from dotenv import load_dotenv

load_dotenv()

try:
    conn = psycopg2.connect(
        host=os.getenv('DB_HOST'),
        port=os.getenv('DB_PORT'),
        dbname=os.getenv('DB_NAME'),
        user=os.getenv('DB_USER'),
        password=os.getenv('DB_PASSWORD')  # Use a nova senha simples
    )
    print("✅ Conexão bem-sucedida com o PostgreSQL!")
    
    # Teste adicional
    cur = conn.cursor()
    cur.execute("SELECT 1")
    print("✅ Teste de consulta bem-sucedido!")
    
    conn.close()
except Exception as e:
    print(f"❌ Erro de conexão: {e}")
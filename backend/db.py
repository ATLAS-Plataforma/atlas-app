import psycopg2

def conectar():
    conn = psycopg2.connect(
        host="localhost",
        database="estoque_db",
        user="postgres",
        password="gemeas@10"
    )

    return conn
import os
import sqlite3
from datetime import datetime

# Rutas robustas relativas a este archivo
BASE_DIR = os.path.dirname(__file__)
DATA_DIR = os.path.join(BASE_DIR, "data")
DB_PATH = os.path.join(DATA_DIR, "restaurante.db")

os.makedirs(DATA_DIR, exist_ok=True)

def conectar():
    """Crea y devuelve la conexión SQLite."""
    return sqlite3.connect(DB_PATH)

def inicializar_bd():
    """Crea tablas si no existen."""
    conn = conectar()
    cur = conn.cursor()

    # Productos (opcional, puedes poblarla aparte)
    cur.execute("""
    CREATE TABLE IF NOT EXISTS productos (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        nombre TEXT NOT NULL UNIQUE,
        precio REAL NOT NULL,
        categoria TEXT DEFAULT 'General',
        activo BOOLEAN DEFAULT 1
    )
    """)

    # Pedidos (detalle por producto)
    cur.execute("""
    CREATE TABLE IF NOT EXISTS pedidos (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        producto TEXT NOT NULL,
        cantidad INTEGER NOT NULL,
        precio REAL NOT NULL,
        fecha TEXT NOT NULL
    )
    """)

    # Ventas (totales por ticket/venta)
    cur.execute("""
    CREATE TABLE IF NOT EXISTS ventas (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        fecha TEXT NOT NULL,
        total REAL NOT NULL
    )
    """)

    conn.commit()
    conn.close()

def registrar_pedido(pedido):
    """
    Registra el pedido (lista de dicts: {producto, cantidad, precio})
    y crea una venta con el total. Devuelve el total.
    """
    if not pedido:
        return 0.0

    fecha = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    total = sum(item["cantidad"] * item["precio"] for item in pedido)

    conn = conectar()
    cur = conn.cursor()

    for item in pedido:
        cur.execute("""
            INSERT INTO pedidos (producto, cantidad, precio, fecha)
            VALUES (?, ?, ?, ?)
        """, (item["producto"], item["cantidad"], item["precio"], fecha))

    cur.execute("INSERT INTO ventas (fecha, total) VALUES (?, ?)", (fecha, total))

    conn.commit()
    conn.close()
    return total

def obtener_balance(fecha_dia=None):
    """
    Suma de ventas. Si fecha_dia='YYYY-MM-DD', filtra por ese día.
    """
    conn = conectar()
    cur = conn.cursor()
    if fecha_dia:
        cur.execute("""
            SELECT SUM(total) FROM ventas
            WHERE DATE(fecha) = DATE(?)
        """, (fecha_dia,))
    else:
        cur.execute("SELECT SUM(total) FROM ventas")
    total = cur.fetchone()[0] or 0.0
    conn.close()
    return float(total)

def obtener_historial(limit=50):
    """Últimas ventas (id, fecha, total) descendente."""
    conn = conectar()
    cur = conn.cursor()
    cur.execute("""
        SELECT id, fecha, total
        FROM ventas
        ORDER BY datetime(fecha) DESC
        LIMIT ?
    """, (limit,))
    rows = cur.fetchall()
    conn.close()
    return rows

if __name__ == "__main__":
    inicializar_bd()
    print("Base de datos creada correctamente ✅")

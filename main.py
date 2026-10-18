from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import sqlite3
from datetime import datetime
from generar_data import generar_datos_ventas

app = FastAPI(title="API Local para Power BI", version="1.0")
DB_NAME = "sales_database.db"

# Permitir conexiones de cualquier origen (CORS) para Power BI
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Estructura de datos para solicitudes POST
class SaleCreate(BaseModel):
    product: str
    category: str
    quantity: int
    unit_price: float

# Crear la base de datos e insertar datos semilla si está vacía
def init_db():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    
    # Crear tabla de ventas
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS sales (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            product TEXT NOT NULL,
            category TEXT NOT NULL,
            quantity INTEGER NOT NULL,
            unit_price REAL NOT NULL,
            total_amount REAL NOT NULL,
            sale_date TEXT NOT NULL
        )
    """)
    
    # Verificar si existen datos
    cursor.execute("SELECT COUNT(*) FROM sales")
    count = cursor.fetchone()[0]
    
    # Si la tabla está vacía, insertar datos iniciales de prueba
    if count == 0:
        #TODO: Generar una opción para que
        initial_data = generar_datos_ventas(1000)  # Generar 1000 registros de ventas de prueba y eliminar los datos preexistentes
        cursor.executemany("""
            INSERT INTO sales (product, category, quantity, unit_price, total_amount, sale_date)
            VALUES (?, ?, ?, ?, ?, ?)
        """, initial_data)
        conn.commit()
        
    conn.close()

@app.on_event("startup")
def startup_event():
    init_db()

# Endpoint principal que consumirá Power BI
@app.get("/api/v1/sales")
def get_sales():
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM sales")
    rows = cursor.fetchall()
    conn.close()
    
    return [dict(row) for row in rows]

# Endpoint opcional para registrar nuevas ventas en tiempo real
@app.post("/api/v1/sales", status_code=201)
def create_sale(sale: SaleCreate):
    total = sale.quantity * sale.unit_price
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO sales (product, category, quantity, unit_price, total_amount, sale_date)
        VALUES (?, ?, ?, ?, ?, ?)
    """, (sale.product, sale.category, sale.quantity, sale.unit_price, total, now))
    conn.commit()
    sale_id = cursor.lastrowid
    conn.close()
    
    return {"id": sale_id, "total_amount": total, "sale_date": now, **sale.model_dump()}
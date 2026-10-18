from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import sqlite3
from datetime import datetime

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
        initial_data = [
            ("Laptop Pro 15", "Electrónica", 2, 1200.00, 2400.00, "2026-10-01 10:15:00"),
            ("Mouse Inalámbrico", "Accesorios", 5, 25.50, 127.50, "2026-10-02 11:30:00"),
            ("Teclado Mecánico", "Accesorios", 3, 85.00, 255.00, "2026-10-03 14:20:00"),
            ("Monitor 27 Pulgadas", "Electrónica", 1, 320.00, 320.00, "2026-10-05 09:45:00"),
            ("Silla Ergonómica", "Mobiliario", 2, 210.00, 420.00, "2026-10-07 16:00:00"),
            ("Escritorio Elevable", "Mobiliario", 1, 450.00, 450.00, "2026-10-10 12:10:00"),
            ("Audífonos Bluetooth", "Electrónica", 4, 60.00, 240.00, "2026-10-12 15:30:00")
        ]
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
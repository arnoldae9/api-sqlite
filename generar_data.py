from datetime import datetime, timedelta
import random


def generar_datos_ventas(num_registros=1000):
    # Catálogo de productos con sus categorías y precios unitarios base
    productos_catalog = [
        ("Laptop Pro 15", "Electrónica", 1200.00),
        ("Mouse Inalámbrico", "Accesorios", 25.50),
        ("Teclado Mecánico", "Accesorios", 85.00),
        ("Monitor 27 Pulgadas", "Electrónica", 320.00),
        ("Silla Ergonómica", "Mobiliario", 210.00),
        ("Escritorio Elevable", "Mobiliario", 450.00),
        ("Audífonos Bluetooth", "Electrónica", 60.00),
        ("Monitor 24 Pulgadas", "Electrónica", 280.00),
        ("Audífonos Candy", "Electrónica", 90.00),
        ("Laptop Gamer", "Electrónica", 1500.00),
        ("Laptop MSI", "Electrónica", 1150.00),
    ]

    # Rango de fechas: Del 01/01/2022 al 31/12/2023
    fecha_inicio = datetime(2022, 1, 1, 8, 0, 0)
    fecha_fin = datetime(2023, 12, 31, 20, 0, 0)
    segundos_totales = int((fecha_fin - fecha_inicio).total_seconds())

    registros = []

    for _ in range(num_registros):
        # 1. Seleccionar producto aleatorio
        producto, categoria, precio_unitario = random.choice(productos_catalog)

        # 2. Generar cantidad aleatoria (entre 1 y 5 unidades)
        cantidad = random.randint(1, 5)

        # 3. Calcular monto total
        monto_total = round(cantidad * precio_unitario, 2)

        # 4. Generar fecha y hora aleatoria entre 2022 y 2023
        segundos_aleatorios = random.randint(0, segundos_totales)
        fecha_aleatoria = fecha_inicio + timedelta(seconds=segundos_aleatorios)
        fecha_str = fecha_aleatoria.strftime("%Y-%m-%d %H:%M:%S")

        # 5. Agregar la tupla al resultado
        registros.append(
            (
                producto,
                categoria,
                cantidad,
                precio_unitario,
                monto_total,
                fecha_str,
            )
        )

    # Ordenar por fecha cronológicamente
    registros.sort(key=lambda x: x[5])

    return registros

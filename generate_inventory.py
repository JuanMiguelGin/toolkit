"""
generate_inventory.py — Generador de inventario de servidores CSV
Lee las categorías reales desde la base de datos Neon (PostgreSQL)
y genera 1000+ filas de servidores ficticios coherentes con el negocio.
"""

import csv
import os
import random
from pathlib import Path

import psycopg2
from dotenv import load_dotenv
from faker import Faker

load_dotenv()

fake = Faker("es_ES")

OUTPUT_PATH = "input/inventory.csv"
FILAS = 1_000

SISTEMAS_OPERATIVOS = [
    "Windows Server 2019",
    "Windows Server 2022",
    "Ubuntu 22.04",
    "Ubuntu 20.04",
    "CentOS 8",
    "Debian 11",
    "Red Hat 9",
]

DEPARTAMENTOS = [
    "Logística",
    "Finanzas",
    "Ventas",
    "IT",
    "Marketing",
    "Operaciones",
    "RRHH",
]

RAM_OPCIONES = [2, 4, 8, 16, 32, 64]
CPU_OPCIONES = [1, 2, 4, 8, 16]


def obtener_categorias_neon() -> list[str]:
    try:
        conn = psycopg2.connect(os.environ["DATABASE_URL"])
        cur = conn.cursor()
        cur.execute("SELECT name FROM categories ORDER BY name;")
        categorias = [fila[0] for fila in cur.fetchall()]
        cur.close()
        conn.close()
        print(f"  ✅  Categorías obtenidas de Neon: {categorias}")
        return categorias
    except Exception as e:
        print(f"  ⚠  No se pudo conectar a Neon: {e}")
        print("  ℹ  Usando categorías por defecto.")
        return ["Electronica", "Hogar", "Deportes", "Alimentacion"]


def _generar_ip() -> str:
    return f"10.{random.randint(0, 5)}.{random.randint(0, 255)}.{random.randint(1, 254)}"


def _generar_fila(idx: int, categorias: list[str]) -> dict:
    return {
        "id": idx,
        "hostname": f"srv-{fake.lexify('????').lower()}-{idx:04d}",
        "ip": _generar_ip(),
        "sistema_operativo": random.choice(SISTEMAS_OPERATIVOS),
        "ram_gb": random.choice(RAM_OPCIONES),
        "cpu_cores": random.choice(CPU_OPCIONES),
        "disco_gb": random.choice([120, 256, 512, 1024, 2048]),
        "departamento": random.choice(DEPARTAMENTOS),
        "categoria_inventario": random.choice(categorias),
        "anio_compra": random.randint(2015, 2024),
        "activo": random.choice([True, True, True, False]),
    }


def generar_csv(ruta: str = OUTPUT_PATH, filas: int = FILAS) -> None:
    categorias = obtener_categorias_neon()
    Path(ruta).parent.mkdir(parents=True, exist_ok=True)
    campos = [
        "id", "hostname", "ip", "sistema_operativo",
        "ram_gb", "cpu_cores", "disco_gb",
        "departamento", "categoria_inventario", "anio_compra", "activo",
    ]
    with open(ruta, "w", newline="", encoding="utf-8-sig") as f:
        writer = csv.DictWriter(f, fieldnames=campos)
        writer.writeheader()
        for i in range(1, filas + 1):
            writer.writerow(_generar_fila(i, categorias))
    print(f"\n  ✅  Inventario generado: {ruta} ({filas} filas)\n")


if __name__ == "__main__":
    generar_csv()
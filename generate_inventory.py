"""
generate_inventory.py — Generador de inventario de servidores CSV
Usa Faker y los datos de la BD del proyecto learning-inventory
(categorías: Electrónica, Hogar, Deportes, Alimentación) para generar
1000+ filas de servidores ficticios coherentes con el negocio.
"""

import csv
import random
from pathlib import Path
from faker import Faker

fake = Faker("es_ES")

OUTPUT_PATH = "input/inventory.csv"
FILAS = 1_000

# Categorías tomadas directamente del seed.sql de learning-inventory
CATEGORIAS = ["Electrónica", "Hogar", "Deportes", "Alimentación"]

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


def _generar_ip() -> str:
    return f"10.{random.randint(0, 5)}.{random.randint(0, 255)}.{random.randint(1, 254)}"


def _generar_fila(idx: int) -> dict:
    categoria = random.choice(CATEGORIAS)
    ram = random.choice(RAM_OPCIONES)
    so = random.choice(SISTEMAS_OPERATIVOS)
    anio = random.randint(2015, 2024)
    return {
        "id": idx,
        "hostname": f"srv-{fake.lexify('????').lower()}-{idx:04d}",
        "ip": _generar_ip(),
        "sistema_operativo": so,
        "ram_gb": ram,
        "cpu_cores": random.choice(CPU_OPCIONES),
        "disco_gb": random.choice([120, 256, 512, 1024, 2048]),
        "departamento": random.choice(DEPARTAMENTOS),
        "categoria_inventario": categoria,
        "anio_compra": anio,
        "activo": random.choice([True, True, True, False]),  # 75 % activos
    }


def generar_csv(ruta: str = OUTPUT_PATH, filas: int = FILAS) -> None:
    """Genera el archivo CSV con `filas` servidores ficticios."""
    Path(ruta).parent.mkdir(parents=True, exist_ok=True)

    campos = [
        "id", "hostname", "ip", "sistema_operativo",
        "ram_gb", "cpu_cores", "disco_gb",
        "departamento", "categoria_inventario", "anio_compra", "activo",
    ]

    with open(ruta, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=campos)
        writer.writeheader()
        for i in range(1, filas + 1):
            writer.writerow(_generar_fila(i))

    print(f"\n  ✅  Inventario generado: {ruta} ({filas} filas)\n")


if __name__ == "__main__":
    generar_csv()

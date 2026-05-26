"""
inventory_manager.py — Gestor de inventario de servidores
Carga el CSV, filtra servidores vulnerables y genera un Excel ejecutivo.
Refleja la estructura del proyecto learning-inventory (categorías de producto).
"""

from __future__ import annotations

from datetime import datetime
from pathlib import Path

import pandas as pd

from generate_inventory import generar_csv

INPUT_CSV = "input/inventory.csv"
OUTPUT_DIR = "output"


def cargar_inventario(ruta: str = INPUT_CSV) -> pd.DataFrame:
    """Carga el CSV de inventario. Si no existe lo genera automáticamente."""
    if not Path(ruta).exists():
        print(f"  ℹ  CSV no encontrado. Generando {ruta}...")
        generar_csv(ruta)
    df = pd.read_csv(ruta)
    df["activo"] = df["activo"].astype(str).str.lower() == "true"
    return df


def filtrar_vulnerables(df: pd.DataFrame) -> pd.DataFrame:
    """
    Devuelve servidores que cumplen al menos uno de estos criterios:
      - SO Windows Server (sin importar versión)
      - RAM < 4 GB
      - Año de compra anterior a 2018 (hardware antiguo)
    """
    mask = (
        df["sistema_operativo"].str.contains("Windows Server", na=False)
        | (df["ram_gb"] < 4)
        | (df["anio_compra"] < 2018)
    )
    return df[mask].copy()


def agrupar_por_departamento(df: pd.DataFrame) -> pd.DataFrame:
    """Cuenta servidores activos por departamento."""
    return (
        df[df["activo"]]
        .groupby("departamento")
        .size()
        .reset_index(name="total_servidores")
        .sort_values("total_servidores", ascending=False)
    )


def agrupar_por_categoria(df: pd.DataFrame) -> pd.DataFrame:
    """Agrupa por categoría de inventario (Electrónica, Hogar, etc.)."""
    return (
        df.groupby("categoria_inventario")
        .agg(
            total=("id", "count"),
            ram_promedio=("ram_gb", "mean"),
            porcentaje_activos=("activo", lambda x: round(x.mean() * 100, 1)),
        )
        .reset_index()
    )


def generar_excel(
    df_vulnerables: pd.DataFrame,
    df_departamentos: pd.DataFrame,
    df_categorias: pd.DataFrame,
) -> str:
    """
    Genera un Excel con tres hojas:
      1. Servidores Vulnerables
      2. Resumen por Departamento
      3. Resumen por Categoría
    Devuelve la ruta del archivo generado.
    """
    Path(OUTPUT_DIR).mkdir(parents=True, exist_ok=True)
    fecha = datetime.now().strftime("%Y%m%d_%H%M")
    ruta_excel = f"{OUTPUT_DIR}/informe_vulnerabilidades_{fecha}.xlsx"

    with pd.ExcelWriter(ruta_excel, engine="openpyxl") as writer:
        # Hoja 1: detalle de servidores vulnerables
        df_vulnerables.to_excel(writer, sheet_name="Servidores Vulnerables", index=False)

        # Hoja 2: agrupación por departamento
        df_departamentos.to_excel(writer, sheet_name="Por Departamento", index=False)

        # Hoja 3: agrupación por categoría de inventario
        df_categorias.to_excel(writer, sheet_name="Por Categoría", index=False)

    return ruta_excel


def ejecutar_analisis(ruta_csv: str = INPUT_CSV) -> None:
    """Punto de entrada desde el menú principal."""
    print(f"\n  📂  Cargando inventario desde '{ruta_csv}'...")
    df = cargar_inventario(ruta_csv)
    print(f"      {len(df)} servidores cargados.")

    # Filtro de vulnerables
    df_vuln = filtrar_vulnerables(df)
    print(f"\n  ⚠  Servidores vulnerables: {len(df_vuln)} "
          f"({len(df_vuln)/len(df)*100:.1f} % del total)")

    # Windows Server
    windows = df_vuln[df_vuln["sistema_operativo"].str.contains("Windows Server", na=False)]
    print(f"     - Windows Server      : {len(windows)}")

    # RAM baja
    ram_baja = df_vuln[df_vuln["ram_gb"] < 4]
    print(f"     - RAM < 4 GB          : {len(ram_baja)}")

    # Antigüedad
    antiguos = df_vuln[df_vuln["anio_compra"] < 2018]
    print(f"     - Compra antes de 2018: {len(antiguos)}")

    # Agrupaciones
    df_depts = agrupar_por_departamento(df)
    df_cats  = agrupar_por_categoria(df)

    print("\n  📊  Servidores activos por departamento:")
    for _, row in df_depts.iterrows():
        print(f"      {row['departamento']:<15} {row['total_servidores']:>4} servidores")

    print("\n  🏷  Resumen por categoría de inventario:")
    for _, row in df_cats.iterrows():
        print(f"      {row['categoria_inventario']:<15} total={row['total']:>4}  "
              f"RAM prom={row['ram_promedio']:.1f} GB  "
              f"activos={row['porcentaje_activos']} %")

    # Generar Excel
    ruta_excel = generar_excel(df_vuln, df_depts, df_cats)
    print(f"\n  📄  Informe Excel generado: {ruta_excel}\n")


if __name__ == "__main__":
    ejecutar_analisis()

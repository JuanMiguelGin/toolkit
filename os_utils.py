"""
os_utils.py — Utilidades del sistema operativo
Comprueba conectividad de red y espacio en disco.
"""

import os
import shutil
import subprocess


UMBRAL_DISCO_PORCENTAJE: float = 20.0


def check_ping(ip: str) -> bool:
    """
    Ejecuta ping -c 1 contra la IP indicada.
    Devuelve True si responde, False en caso contrario.
    """
    try:
        resultado = subprocess.run(
            ["ping", "-c", "1", "-W", "2", ip],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            timeout=5,
        )
        return resultado.returncode == 0
    except (subprocess.TimeoutExpired, FileNotFoundError):
        return False


def check_disk(particion: str = "/") -> None:
    """
    Comprueba el espacio libre en la partición indicada.
    Lanza una alerta si el espacio libre es inferior al 20 %.
    """
    if not os.path.exists(particion):
        print(f"  ⚠  La partición '{particion}' no existe.")
        return

    total, usado, libre = shutil.disk_usage(particion)

    total_gb: float = total / (1024 ** 3)
    libre_gb: float = libre / (1024 ** 3)
    porcentaje_libre: float = (libre / total) * 100

    print(f"\n  📀  Disco [{particion}]")
    print(f"      Total : {total_gb:.1f} GB")
    print(f"      Libre : {libre_gb:.1f} GB  ({porcentaje_libre:.1f} %)")

    if porcentaje_libre < UMBRAL_DISCO_PORCENTAJE:
        print(f"  🚨  ALERTA: menos del {UMBRAL_DISCO_PORCENTAJE:.0f} % de espacio libre.")
    else:
        print(f"  ✅  Espacio en disco OK.")

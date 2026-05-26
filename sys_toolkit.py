"""
sys_toolkit.py — Menú principal del Kit de Herramientas para Sysadmin
Proporciona acceso CLI a todos los módulos del toolkit.
"""

import sys
from typing import NoReturn


def print_menu() -> None:
    """Muestra el menú principal en consola."""
    print("\n" + "=" * 55)
    print("  🛠  SYS-TOOLKIT — Kit de Herramientas Sysadmin")
    print("=" * 55)
    print("  [1] Auditor de seguridad SSH (log_parser)")
    print("  [2] Geolocalizacion de IPs sospechosas (threat_intel)")
    print("  [3] Comprobaciones del sistema operativo (os_utils)")
    print("  [4] Generar inventario de productos CSV (generate_inventory)")
    print("  [5] Gestionar inventario y generar Excel (inventory_manager)")
    print("  [6] Modelo OOP de dispositivos de red (network_models)")
    print("  [0] Salir")
    print("-" * 55)


def run() -> NoReturn:
    """Bucle principal del menú interactivo."""
    while True:
        print_menu()
        choice: str = input("  Selecciona una opción: ").strip()

        if choice == "1":
            from log_parser import analizar_logs
            analizar_logs()

        elif choice == "2":
            from threat_intel import mostrar_tabla_amenazas
            mostrar_tabla_amenazas()

        elif choice == "3":
            from os_utils import check_ping, check_disk
            ip: str = input("  IP a hacer ping: ").strip()
            resultado: bool = check_ping(ip)
            print(f"  → Ping a {ip}: {'✅ OK' if resultado else '❌ Sin respuesta'}")
            particion: str = input("  Partición a comprobar (ej. /): ").strip()
            check_disk(particion)

        elif choice == "4":
            from generate_inventory import generar_csv
            generar_csv()

        elif choice == "5":
            from inventory_manager import ejecutar_analisis
            ejecutar_analisis()

        elif choice == "6":
            from network_models import demo_dispositivos
            demo_dispositivos()

        elif choice == "0":
            print("\n  👋  Hasta luego.\n")
            sys.exit(0)

        else:
            print("  ⚠  Opción no válida. Inténtalo de nuevo.")


if __name__ == "__main__":
    run()

"""
threat_intel.py — Inteligencia de amenazas
Geolocaliza IPs sospechosas usando ipinfo.io y muestra tabla resumen.
"""

import requests
from log_parser import parsear_log


IPINFO_URL = "https://ipinfo.io/{ip}/json"
TIMEOUT_SEG = 5


def geolocalizacion_ip(ip: str) -> dict[str, str]:
    """
    Consulta ipinfo.io para obtener país y organización de una IP.
    Devuelve un dict con 'pais' y 'org'. En caso de error devuelve 'N/A'.
    """
    try:
        respuesta = requests.get(IPINFO_URL.format(ip=ip), timeout=TIMEOUT_SEG)
        respuesta.raise_for_status()
        datos = respuesta.json()
        return {
            "pais": datos.get("country", "N/A"),
            "ciudad": datos.get("city", "N/A"),
            "org": datos.get("org", "N/A"),
        }
    except requests.RequestException as err:
        return {"pais": "N/A", "ciudad": "N/A", "org": f"Error: {err}"}


def mostrar_tabla_amenazas() -> None:
    """
    Obtiene las IPs del log, las geolocaliza y muestra una tabla
    con IP, intentos, país y organización.
    """
    ruta: str = input("  Ruta del log [input/auth.log]: ").strip() or "input/auth.log"
    contador: dict[str, int] = parsear_log(ruta)

    if not contador:
        print("  ✅  No hay IPs sospechosas que analizar.")
        return

    print(f"\n  🌍  Geolocalizando {len(contador)} IPs... (puede tardar unos segundos)\n")

    cabecera = f"  {'IP':<20} {'Intentos':>8}  {'País':<6}  {'Organización'}"
    print(cabecera)
    print("  " + "-" * 65)

    for ip, intentos in contador.items():
        geo = geolocalizacion_ip(ip)
        org_corta: str = geo["org"][:35] if len(geo["org"]) > 35 else geo["org"]
        print(f"  {ip:<20} {intentos:>8}  {geo['pais']:<6}  {org_corta}")

    print()

"""
log_parser.py — Analizador de logs SSH
Lee auth.log, extrae IPs con intentos fallidos y las cuenta.
"""

import re
from collections import defaultdict
from pathlib import Path


LOG_PATH: str = "input/auth.log"

# Regex para extraer la IP de una línea de fallo SSH
_RE_IP = re.compile(r"Failed password for .+ from (\d{1,3}(?:\.\d{1,3}){3})")


def _generar_log_simulado(ruta: str) -> None:
    """Crea un auth.log de ejemplo si no existe."""
    lineas = [
        "May 26 10:01:01 server sshd[1234]: Failed password for root from 192.168.1.10 port 22 ssh2",
        "May 26 10:01:05 server sshd[1235]: Accepted password for admin from 10.0.0.5 port 22 ssh2",
        "May 26 10:02:11 server sshd[1236]: Failed password for root from 192.168.1.10 port 22 ssh2",
        "May 26 10:03:20 server sshd[1237]: Failed password for ubuntu from 203.0.113.99 port 22 ssh2",
        "May 26 10:04:01 server sshd[1238]: Failed password for admin from 192.168.1.10 port 22 ssh2",
        "May 26 10:05:30 server sshd[1239]: Failed password for root from 198.51.100.7 port 22 ssh2",
        "May 26 10:06:00 server sshd[1240]: Failed password for root from 203.0.113.99 port 22 ssh2",
        "May 26 10:07:15 server sshd[1241]: Accepted publickey for deploy from 10.0.0.1 port 22 ssh2",
        "May 26 10:08:44 server sshd[1242]: Failed password for root from 198.51.100.7 port 22 ssh2",
        "May 26 10:09:00 server sshd[1243]: Failed password for root from 198.51.100.7 port 22 ssh2",
    ]
    Path(ruta).parent.mkdir(parents=True, exist_ok=True)
    with open(ruta, "w") as f:
        f.write("\n".join(lineas) + "\n")
    print(f"  ℹ  Log simulado creado en '{ruta}'.")


def parsear_log(ruta: str = LOG_PATH) -> dict[str, int]:
    """
    Lee el archivo de log línea a línea y cuenta los intentos fallidos
    de SSH por IP. Devuelve un dict {ip: intentos}.
    """
    if not Path(ruta).exists():
        _generar_log_simulado(ruta)

    ips_fallidas: set[str] = set()
    contador: dict[str, int] = defaultdict(int)

    with open(ruta, "r", encoding="utf-8", errors="ignore") as fh:
        for linea in fh:
            linea = linea.strip()
            match = _RE_IP.search(linea)
            if match:
                ip: str = match.group(1)
                ips_fallidas.add(ip)
                contador[ip] += 1

    return dict(sorted(contador.items(), key=lambda x: x[1], reverse=True))


def analizar_logs() -> None:
    """Punto de entrada desde el menú principal."""
    ruta: str = input(f"  Ruta del log [{LOG_PATH}]: ").strip() or LOG_PATH
    resultados: dict[str, int] = parsear_log(ruta)

    if not resultados:
        print("  ✅  No se encontraron intentos fallidos.")
        return

    print(f"\n  🔍  IPs con intentos fallidos de SSH ({len(resultados)} únicas):\n")
    print(f"  {'IP':<20} {'Intentos':>8}")
    print("  " + "-" * 30)
    for ip, intentos in resultados.items():
        alerta = " 🚨" if intentos >= 3 else ""
        print(f"  {ip:<20} {intentos:>8}{alerta}")
    print()

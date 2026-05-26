"""
test_toolkit.py — Tests unitarios del sys-toolkit
Ejecutar con: pytest test_toolkit.py -v
"""

import sys
import os

sys.path.insert(0, os.path.dirname(__file__))

import pytest
from log_parser import parsear_log
from os_utils import check_ping, check_disk
from network_models import Router, Server
from generate_inventory import _generar_fila
import pandas as pd
from inventory_manager import filtrar_vulnerables, agrupar_por_departamento


# ──────────────────────────────────────────────
# log_parser
# ──────────────────────────────────────────────

class TestLogParser:
    def test_conteo_ips_correcto(self, tmp_path):
        """El parser cuenta correctamente los intentos por IP."""
        log = tmp_path / "auth.log"
        log.write_text(
            "May 26 10:01:01 server sshd[1]: Failed password for root from 1.2.3.4 port 22 ssh2\n"
            "May 26 10:01:05 server sshd[2]: Failed password for root from 1.2.3.4 port 22 ssh2\n"
            "May 26 10:02:00 server sshd[3]: Failed password for root from 5.6.7.8 port 22 ssh2\n"
        )
        resultado = parsear_log(str(log))
        assert resultado["1.2.3.4"] == 2
        assert resultado["5.6.7.8"] == 1

    def test_lineas_exitosas_ignoradas(self, tmp_path):
        """Las líneas 'Accepted' no se cuentan como fallos."""
        log = tmp_path / "auth.log"
        log.write_text(
            "May 26 10:05:00 server sshd[5]: Accepted password for admin from 9.9.9.9 port 22 ssh2\n"
        )
        resultado = parsear_log(str(log))
        assert "9.9.9.9" not in resultado

    def test_log_vacio(self, tmp_path):
        """Un log vacío devuelve un diccionario vacío."""
        log = tmp_path / "auth.log"
        log.write_text("")
        resultado = parsear_log(str(log))
        assert resultado == {}

    def test_sin_duplicados_en_ips(self, tmp_path):
        """El set de IPs no tiene duplicados (siempre se cumple con dict)."""
        log = tmp_path / "auth.log"
        log.write_text(
            "May 26 10:01:01 server sshd[1]: Failed password for root from 1.2.3.4 port 22 ssh2\n"
            "May 26 10:01:02 server sshd[2]: Failed password for root from 1.2.3.4 port 22 ssh2\n"
            "May 26 10:01:03 server sshd[3]: Failed password for root from 1.2.3.4 port 22 ssh2\n"
        )
        resultado = parsear_log(str(log))
        assert len(resultado) == 1  # solo una IP única


# ──────────────────────────────────────────────
# os_utils
# ──────────────────────────────────────────────

class TestOsUtils:
    def test_ping_localhost(self, monkeypatch):
        """El ping a localhost devuelve True cuando el subprocess retorna 0."""
        import subprocess

        class FakeResult:
            returncode = 0

        monkeypatch.setattr(subprocess, "run", lambda *a, **kw: FakeResult())
        assert check_ping("127.0.0.1") is True

    def test_ping_ip_invalida(self):
        """Una IP inválida/inalcanzable debe devolver False."""
        assert check_ping("192.0.2.255") is False  # TEST-NET reservada

    def test_check_disk_raiz_no_falla(self):
        """check_disk no lanza excepción en la partición raíz."""
        try:
            check_disk("/")
        except Exception as exc:
            pytest.fail(f"check_disk('/') lanzó una excepción inesperada: {exc}")


# ──────────────────────────────────────────────
# network_models
# ──────────────────────────────────────────────

class TestNetworkModels:
    def test_router_hereda_networkdevice(self):
        from network_models import NetworkDevice
        r = Router("gw-test", "10.0.0.1", "AA:BB:CC:DD:EE:FF", "Cisco", 4)
        assert isinstance(r, NetworkDevice)

    def test_server_hereda_networkdevice(self):
        from network_models import NetworkDevice
        s = Server("srv-test", "10.0.0.2", "AA:BB:CC:DD:EE:00",
                   "Ubuntu 22.04", 8, "Electrónica")
        assert isinstance(s, NetworkDevice)

    def test_audit_device_se_ejecuta(self, capsys):
        r = Router("gw-test", "10.0.0.1", "AA:BB:CC:DD:EE:FF", "Cisco", 4)
        r.audit_device()
        captured = capsys.readouterr()
        assert "gw-test" in captured.out

    def test_server_ram_baja_aviso(self, capsys):
        """Un servidor con < 4 GB de RAM debe mostrar la alerta de RAM."""
        s = Server("srv-viejo", "10.0.0.3", "AA:BB:CC:DD:EE:03",
                   "Debian 11", 2, "Hogar")
        s.audit_device()
        captured = capsys.readouterr()
        assert "RAM < 4" in captured.out


# ──────────────────────────────────────────────
# inventory_manager / generate_inventory
# ──────────────────────────────────────────────

class TestInventory:
    @pytest.fixture
    def df_muestra(self):
        """DataFrame de prueba con las categorías de learning-inventory."""
        data = {
            "id": [1, 2, 3, 4, 5],
            "hostname": ["srv-a", "srv-b", "srv-c", "srv-d", "srv-e"],
            "ip": ["10.0.0.1", "10.0.0.2", "10.0.0.3", "10.0.0.4", "10.0.0.5"],
            "sistema_operativo": [
                "Windows Server 2019", "Ubuntu 22.04",
                "Windows Server 2022", "CentOS 8", "Debian 11",
            ],
            "ram_gb": [16, 2, 8, 4, 32],
            "cpu_cores": [4, 2, 8, 4, 16],
            "disco_gb": [512, 256, 1024, 512, 2048],
            "departamento": ["IT", "Ventas", "IT", "RRHH", "Finanzas"],
            "categoria_inventario": [
                "Electrónica", "Hogar", "Deportes", "Alimentación", "Electrónica"
            ],
            "año_compra": [2020, 2016, 2021, 2019, 2022],
            "activo": [True, True, False, True, True],
        }
        return pd.DataFrame(data)

    def test_filtrar_windows_server(self, df_muestra):
        """Detecta correctamente los servidores Windows."""
        resultado = filtrar_vulnerables(df_muestra)
        hostnames = resultado["hostname"].tolist()
        assert "srv-a" in hostnames
        assert "srv-c" in hostnames

    def test_filtrar_ram_baja(self, df_muestra):
        """Detecta servidores con menos de 4 GB de RAM."""
        resultado = filtrar_vulnerables(df_muestra)
        assert "srv-b" in resultado["hostname"].tolist()

    def test_filtrar_antiguos(self, df_muestra):
        """Detecta servidores comprados antes de 2018."""
        resultado = filtrar_vulnerables(df_muestra)
        assert "srv-b" in resultado["hostname"].tolist()  # año_compra=2016

    def test_no_filtra_servidores_ok(self, df_muestra):
        """Un servidor Ubuntu moderno con buena RAM no debe aparecer."""
        resultado = filtrar_vulnerables(df_muestra)
        # srv-e: Debian 11, 32 GB RAM, 2022 → no vulnerable
        assert "srv-e" not in resultado["hostname"].tolist()

    def test_agrupacion_departamento(self, df_muestra):
        """La agrupación por departamento cuenta solo servidores activos."""
        resultado = agrupar_por_departamento(df_muestra)
        it = resultado[resultado["departamento"] == "IT"]["total_servidores"].values
        # srv-c está inactivo → solo srv-a cuenta para IT
        assert it[0] == 1

    def test_generador_fila_campos_completos(self):
        """Cada fila generada tiene todos los campos necesarios."""
        fila = _generar_fila(1, ["Electronica", "Hogar"])
        for campo in ["id", "hostname", "ip", "sistema_operativo", "ram_gb",
                      "departamento", "categoria_inventario", "año_compra", "activo"]:
            assert campo in fila

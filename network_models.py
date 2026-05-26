"""
network_models.py — Modelo OOP de dispositivos de red
Clases base y especializadas con polimorfismo para auditoría.
"""


class NetworkDevice:
    """Clase base que representa cualquier dispositivo de red."""

    def __init__(self, hostname: str, ip: str, mac: str) -> None:
        self.hostname: str = hostname
        self.ip: str = ip
        self.mac: str = mac

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}(hostname={self.hostname!r}, ip={self.ip!r})"

    def audit_device(self) -> None:
        """Método polimórfico: cada subclase implementa sus propias directrices."""
        print(f"\n  🔎  Auditoría de {self.hostname} [{self.ip}]")
        print(f"      MAC: {self.mac}")


class Router(NetworkDevice):
    """Router de red — dispositivo de capa 3."""

    def __init__(self, hostname: str, ip: str, mac: str, modelo: str, interfaces: int) -> None:
        super().__init__(hostname, ip, mac)
        self.modelo: str = modelo
        self.interfaces: int = interfaces

    def audit_device(self) -> None:
        super().audit_device()
        print(f"      Tipo     : Router ({self.modelo}, {self.interfaces} interfaces)")
        print("      Directrices de seguridad:")
        print("        • Deshabilitar acceso Telnet; usar SSH v2 únicamente")
        print("        • Activar ACLs en todas las interfaces de entrada")
        print("        • Revisar tablas de enrutamiento cada semana")
        print("        • Cambiar credenciales por defecto y activar 2FA")


class Server(NetworkDevice):
    """Servidor — puede ser físico o virtual."""

    def __init__(
        self,
        hostname: str,
        ip: str,
        mac: str,
        os_name: str,
        ram_gb: int,
        categoria: str,
    ) -> None:
        super().__init__(hostname, ip, mac)
        self.os_name: str = os_name
        self.ram_gb: int = ram_gb
        self.categoria: str = categoria  # ej: "Electrónica", "Hogar"...

    def audit_device(self) -> None:
        super().audit_device()
        print(f"      Tipo     : Servidor ({self.os_name}, {self.ram_gb} GB RAM)")
        print(f"      Categoría inventario: {self.categoria}")
        print("      Directrices de seguridad:")
        print("        • Aplicar últimas actualizaciones de seguridad del SO")
        print("        • Revisar usuarios con privilegios sudo/administrador")
        print("        • Auditar puertos abiertos con nmap o ss -tuln")
        if self.ram_gb < 4:
            print("        • ⚠  RAM < 4 GB: candidato a actualización urgente")
        if "Windows" in self.os_name:
            print("        • Verificar que Windows Defender está activo y actualizado")


def demo_dispositivos() -> None:
    """Instancia dispositivos de ejemplo y ejecuta auditorías."""
    dispositivos: list[NetworkDevice] = [
        Router("gw-principal", "10.0.0.1", "AA:BB:CC:DD:EE:01", "Cisco ISR 4331", 4),
        Server("srv-electrónica", "10.0.1.10", "AA:BB:CC:DD:EE:10",
               "Ubuntu 22.04", 16, "Electrónica"),
        Server("srv-hogar", "10.0.1.20", "AA:BB:CC:DD:EE:20",
               "Windows Server 2019", 2, "Hogar"),
        Server("srv-deportes", "10.0.1.30", "AA:BB:CC:DD:EE:30",
               "CentOS 8", 8, "Deportes"),
    ]

    print(f"\n  📡  Inventario de red: {len(dispositivos)} dispositivos\n")
    for dispositivo in dispositivos:
        dispositivo.audit_device()
    print()

# SYS-TOOLKIT — Documentación Técnica

## ¿Por qué Python además de Bash?

Un administrador de sistemas moderno necesita Python **además** de Bash por varias razones:

- **Manipulación de datos estructurados**: Bash no puede procesar CSV, JSON o Excel de forma nativa. Python con pandas lo hace en pocas líneas.
- **Integración con APIs REST**: consumir ipinfo.io o cualquier API con `requests` es trivial en Python; en Bash requiere `curl` + `jq` y pierde legibilidad rápidamente.
- **Mantenibilidad**: los scripts largos de Bash se vuelven frágiles. Python permite estructurar el código con funciones, clases y módulos.
- **Testing**: `pytest` ofrece un framework de pruebas completo que no existe en Bash.
- **Portabilidad**: Python corre igual en Linux, macOS y Windows; Bash varía entre sistemas.

---

## Relación con la BD de learning-inventory

Este toolkit reutiliza el modelo de datos del proyecto **learning-inventory** (Next.js + Neon PostgreSQL):

| Tabla original (SQL)  | Equivalente en toolkit (CSV/Python) |
|-----------------------|--------------------------------------|
| `categories.name`     | `categoria_inventario` en el CSV     |
| `products.name`       | `hostname` del servidor              |
| `products.stock`      | `activo` (disponibilidad)            |
| `products.price`      | `ram_gb` / `disco_gb` (recursos)     |

Las **4 categorías** del seed SQL (`Electrónica`, `Hogar`, `Deportes`, `Alimentación`) se preservan en el campo `categoria_inventario` del inventario de servidores, permitiendo agrupar y filtrar la infraestructura del mismo modo que se agrupan los productos en la tienda.

---

## Estructura del proyecto

```
sys_toolkit/
├── sys_toolkit.py         # Menú CLI principal
├── os_utils.py            # Ping + comprobación de disco
├── log_parser.py          # Auditor SSH (auth.log)
├── threat_intel.py        # Geolocalización de IPs con ipinfo.io
├── network_models.py      # OOP: NetworkDevice, Router, Server
├── generate_inventory.py  # Genera inventory.csv (1 000+ filas)
├── inventory_manager.py   # Análisis pandas + exportación Excel
├── test_toolkit.py        # Tests unitarios (pytest)
├── requirements.txt
├── .gitignore
├── docs/
│   └── python-sysadmin.md
├── input/                 # auth.log y inventory.csv (generados)
└── output/                # Informes Excel (generados)
```

---

## Módulos

### `os_utils.py`
- `check_ping(ip: str) → bool` — ping -c 1, devuelve True/False.
- `check_disk(particion: str)` — alerta si espacio libre < 20 %.

### `log_parser.py`
- `parsear_log(ruta: str) → dict[str, int]` — lee auth.log con `with open` (sin cargar todo en RAM), extrae IPs con regex, usa `set` para unicidad y `dict` para conteo.

### `threat_intel.py`
- `geolocalizacion_ip(ip: str) → dict` — GET a `ipinfo.io/{ip}/json`, parsea país y org.
- `mostrar_tabla_amenazas()` — combina log_parser + geolocalizacion en tabla CLI.

### `network_models.py`
- `NetworkDevice` — clase base con `hostname`, `ip`, `mac` y `audit_device()`.
- `Router(NetworkDevice)` — añade `modelo` e `interfaces`; directrices específicas de router.
- `Server(NetworkDevice)` — añade `os_name`, `ram_gb`, `categoria`; polimorfismo para detectar RAM baja y Windows.

**¿Por qué OOP para el inventario de red?**  
La herencia permite añadir nuevos tipos de dispositivo (Switch, Firewall) sin modificar el código existente (principio Open/Closed). El polimorfismo de `audit_device()` garantiza que cada dispositivo aplique sus propias reglas sin condicionales en el código cliente.

### `generate_inventory.py`
- Usa `Faker`, `csv` y `random` para generar 1 000 filas.
- Las categorías provienen directamente del `seed.sql` del proyecto learning-inventory.

### `inventory_manager.py`
- `cargar_inventario()` — `pd.read_csv`, genera el CSV si no existe.
- `filtrar_vulnerables()` — Windows Server **o** RAM < 4 GB **o** compra < 2018.
- `agrupar_por_departamento()` — `groupby` + `size`, solo activos.
- `agrupar_por_categoria()` — agrupa por `categoria_inventario` (refleja la BD).
- `generar_excel()` — tres hojas con `pd.ExcelWriter` + openpyxl.

---

## Ejecución

```bash
# Instalar dependencias
python -m venv venv && source venv/bin/activate
pip install -r requirements.txt

# Menú interactivo
python sys_toolkit.py

# Generar sólo el CSV
python generate_inventory.py

# Generar sólo el informe Excel
python inventory_manager.py

# Ejecutar tests
pytest test_toolkit.py -v
```

---

## Tests (`test_toolkit.py`)

| Test | Qué verifica |
|------|--------------|
| `test_conteo_ips_correcto` | El contador de IPs es preciso |
| `test_lineas_exitosas_ignoradas` | Los logins OK no se cuentan |
| `test_log_vacio` | Log vacío → dict vacío |
| `test_sin_duplicados_en_ips` | La IP siempre aparece una vez como clave |
| `test_ping_localhost` | Ping a 127.0.0.1 devuelve True |
| `test_ping_ip_invalida` | IP inalcanzable devuelve False |
| `test_check_disk_raiz_no_falla` | check_disk('/') no lanza excepción |
| `test_router_hereda_networkdevice` | Router es subclase de NetworkDevice |
| `test_server_hereda_networkdevice` | Server es subclase de NetworkDevice |
| `test_audit_device_se_ejecuta` | audit_device imprime el hostname |
| `test_server_ram_baja_aviso` | Alerta visible cuando RAM < 4 GB |
| `test_filtrar_windows_server` | Detecta todos los Windows Server |
| `test_filtrar_ram_baja` | Detecta servidores con < 4 GB RAM |
| `test_filtrar_antiguos` | Detecta compras anteriores a 2018 |
| `test_no_filtra_servidores_ok` | Servidor sano no aparece en vulnerables |
| `test_agrupacion_departamento` | Cuenta solo servidores activos |
| `test_generador_fila_campos_completos` | Cada fila generada tiene todos los campos |

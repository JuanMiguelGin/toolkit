# 🛠 Toolkit para Administradores de Sistemas
 
Este proyecto es un kit de herramientas hecho en Python pensado para un administrador de sistemas. Incluye varias utilidades que se usan en el día a día: revisar quién intenta entrar a un servidor por SSH, comprobar el estado del disco, geolocalizar IPs sospechosas y gestionar un inventario de servidores conectado a una base de datos real.
 
Todo se maneja desde un menú interactivo en la terminal.
 
---
 
## ¿Por qué Python y no solo Bash?
 
Bash está muy bien para tareas rápidas y simples, pero cuando necesitas procesar archivos CSV, conectarte a una base de datos, consumir APIs o generar informes en Excel, Python es mucho más cómodo y el código queda más claro y fácil de mantener. Además, con Python puedes escribir tests automáticos para asegurarte de que todo funciona correctamente, algo que en Bash es bastante complicado.
 
---
 
## Cómo ejecutarlo
 
**1. Crea el entorno virtual e instala las dependencias:**
```
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
```
 
**2. Crea el archivo `.env` con tu conexión a la base de datos:**
```
DATABASE_URL=postgresql://usuario:contraseña@host/database
```
 
**3. Arranca el menú:**
```
python sys_toolkit.py
```
 
---
 
## Qué hace cada opción del menú
 
### [1] Auditor de seguridad SSH
Lee el archivo `auth.log` y detecta qué IPs han intentado entrar al servidor por SSH sin éxito. Las guarda sin duplicados y cuenta cuántas veces lo ha intentado cada una.
 
### [2] Geolocalización de IPs sospechosas
Coge las IPs detectadas por el auditor y consulta la API pública de ipinfo.io para saber de qué país y empresa viene cada ataque. Muestra una tabla en la terminal con toda esa información junta.
 
### [3] Comprobaciones del sistema
Dos herramientas básicas:
- Hace ping a una IP y te dice si está activa o no
- Comprueba el espacio libre en disco y lanza una alerta si queda menos del 20%
### [4] Generar inventario CSV
Se conecta a la base de datos real (Neon PostgreSQL) del proyecto **learning-inventory**, obtiene las categorías reales (Alimentación, Deportes, Electrónica, Hogar) y genera un archivo CSV con 1000 servidores ficticios usando esas categorías. El archivo se guarda en `input/inventory.csv`.
 
### [5] Gestionar inventario y generar Excel
Carga el CSV generado, filtra los servidores que pueden ser un problema de seguridad o que están obsoletos:
- Servidores con Windows Server (cualquier versión)
- Servidores con menos de 4 GB de RAM
- Servidores comprados antes de 2018
Luego agrupa los equipos por departamento y por categoría, y genera un informe Excel con tres hojas en la carpeta `output/`. Ese Excel está pensado para entregárselo a gerencia.
 
### [6] Modelo OOP de dispositivos de red
Muestra un ejemplo de cómo organizar el inventario de red de una empresa usando programación orientada a objetos. Hay una clase base `NetworkDevice` de la que heredan `Router` y `Server`, cada uno con sus propias directrices de seguridad. Si mañana necesitas añadir un nuevo tipo de dispositivo solo tienes que crear una nueva clase sin tocar el resto del código.
 
---
 
## Conexión con la base de datos
 
Este toolkit se conecta a la base de datos PostgreSQL del proyecto **learning-inventory** alojada en Neon. Las categorías de productos (Alimentación, Deportes, Electrónica, Hogar) se usan directamente para clasificar los servidores del inventario, de forma que la infraestructura IT queda organizada siguiendo la misma estructura que el negocio.
 
Si la conexión falla por algún motivo, el script usa unas categorías por defecto y sigue funcionando igualmente.
 
---
 
## Estructura del proyecto
 
```
toolkit/
├── sys_toolkit.py         # Menú principal
├── os_utils.py            # Ping y comprobación de disco
├── log_parser.py          # Auditor de logs SSH
├── threat_intel.py        # Geolocalización de IPs
├── network_models.py      # Clases de dispositivos de red
├── generate_inventory.py  # Genera el CSV conectándose a Neon
├── inventory_manager.py   # Análisis con pandas y exportación a Excel
├── test_toolkit.py        # Tests unitarios
├── requirements.txt       # Dependencias del proyecto
├── .gitignore             # Excluye venv/ y .env
├── input/                 # Archivos de entrada (CSV generado)
└── output/                # Archivos de salida (Excel generado)
```
 
---
 
## Tests unitarios
 
El proyecto incluye 17 tests automáticos que verifican que todo funciona correctamente. Para ejecutarlos:
 
```
pytest test_toolkit.py -v
```
 
Los tests comprueban cosas como:
- Que el auditor SSH cuenta bien los intentos fallidos por IP
- Que los logins correctos no se cuentan como ataques
- Que el filtro de servidores vulnerables detecta correctamente Windows Server, poca RAM y hardware antiguo
- Que las clases de red heredan correctamente y muestran las alertas esperadas
Resultado esperado: **17 passed**.
 
---
 
## Dependencias principales
 
| Librería | Para qué se usa |
|---|---|
| `pandas` | Cargar y filtrar el inventario CSV |
| `openpyxl` | Generar el informe Excel |
| `faker` | Generar datos ficticios de servidores |
| `requests` | Consultar la API de ipinfo.io |
| `psycopg2-binary` | Conectarse a la base de datos PostgreSQL de Neon |
| `python-dotenv` | Leer las variables de entorno del archivo `.env` |
| `pytest` | Ejecutar los tests unitarios |
| `schedule` | Programar ejecuciones automáticas |
# OBJECTRA

Aplicación web académica para detectar y segmentar objetos con la cámara o una imagen. Usa Django, PostgreSQL y YOLO11s-seg con OpenVINO. La interfaz permite elegir tres calidades, ajustar la confianza, comparar una imagen antes y después del análisis y consultar el historial de capturas guardadas.

## Probar la demo en Windows

Con el paquete **OBJECTRA-Demo-Windows.zip** del equipo:

1. Extrae el ZIP completo en una carpeta donde puedas escribir.
2. Haz doble clic en **Iniciar OBJECTRA.cmd**. En el primer arranque necesitas Internet y WinGet para que el iniciador prepare los componentes que falten.
3. Deja la ventana abierta. Cuando arranque, abre [OBJECTRA en localhost](http://127.0.0.1:8000/) si el navegador no se abrió automáticamente.

El paquete ya incluye los modelos OpenVINO. La copia de código que ofrece **Code → Download ZIP** de GitHub requiere la configuración de desarrollo indicada abajo. El instalador en PowerShell se desarrolla en el [PR #6](https://github.com/Sshadowcitoo/OBJECTRA/pull/6).

### Instalación asistida con PowerShell

Esta rama incluye `setup-local.ps1`. En Windows de 64 bits con Internet y WinGet, ejecútalo desde la carpeta del proyecto:

```powershell
.\setup-local.ps1
```

El script prepara los componentes que falten y reutiliza la configuración existente. Para copiar exportaciones ya preparadas, usa `-ModelsSource "C:\ruta\a\los-modelos"`. Si faltan modelos y no se indica una carpeta, el script genera las exportaciones desde YOLO11s-seg oficial. Para preparar sin arrancar, añade `-NoStart`. La demo con doble clic se entrega en el ZIP descrito arriba.

## Ejecutar desde el repositorio

Requisitos de la configuración documentada para Windows: Python 3.13, PostgreSQL 14 o posterior, Git y las [tres exportaciones OpenVINO](models/README.md).

```powershell
git clone https://github.com/Sshadowcitoo/OBJECTRA.git
cd OBJECTRA
py -3.13 -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
New-Item -ItemType Directory -Force .local
Copy-Item .local.example\database.json .local\database.json
```

En una instalación nueva, crea en PostgreSQL un rol con inicio de sesión llamado `objectra` y una base `objectra` de su propiedad. Para ejecutar las pruebas con PostgreSQL, crea también `test_objectra` con el mismo propietario. Configura las credenciales en `.local/database.json`. Las variables `DB_*` tienen prioridad sobre el JSON. El archivo `.env.example` sirve de referencia y Django no lo carga automáticamente.

Coloca las tres exportaciones bajo `models/`, deja PostgreSQL activo y ejecuta:

```powershell
.\start-local.ps1
```

El script comprueba la conexión, aplica las migraciones pendientes y arranca Django en [127.0.0.1:8000](http://127.0.0.1:8000/). Si ya tienes un entorno de Python con las dependencias, puedes pasar su ejecutable con `-Python`.

## Uso y verificación

- **Explorar la detección** analiza una imagen de ejemplo y abre el comparador. El ejemplo no se puede guardar.
- **Encender cámara** usa la cámara del navegador. Puedes ajustar calidad y confianza, guardar una captura y verla en **Historial**.
- **Subir imagen** analiza una foto propia. Puedes comparar el resultado y guardarlo.

Consulta el [contrato de la API](docs/CONTRATO.md), la [guía de verificación](docs/VERIFICACION_BASE.md) y el [guion de demostración](docs/GUION_VIDEO.md). Mantén fuera de Git las credenciales, las bases locales, los entornos virtuales y los pesos.

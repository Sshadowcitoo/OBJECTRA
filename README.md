# OBJECTRA

Aplicación web académica para detectar y segmentar objetos con la cámara o una imagen. Usa Django, PostgreSQL y YOLO11s-seg con OpenVINO. La interfaz permite elegir tres calidades, ajustar la confianza, comparar una imagen antes y después del análisis y consultar el historial de capturas guardadas.

## Probar la demo en Windows

Descarga **OBJECTRA-Demo-Windows.zip** desde la [release v0.1.0-demo](https://github.com/Sshadowcitoo/OBJECTRA/releases/tag/v0.1.0-demo). El paquete incluye las tres exportaciones de EVA (320, 480 y 640) y un iniciador para Windows x64.

1. Extrae el ZIP completo en una carpeta local donde puedas escribir.
2. Haz doble clic en **Iniciar OBJECTRA.cmd**. El primer arranque requiere Internet y, si faltan componentes del sistema, WinGet. El iniciador prepara Python, las dependencias de la aplicación y PostgreSQL local según haga falta.
3. Cuando la consola indique que arrancó, abre [OBJECTRA en localhost](http://127.0.0.1:8000/) y deja la ventana abierta. Para detenerlo, pulsa **Ctrl+C** en la consola.

La verificación en una PC Windows limpia sigue pendiente. **Code → Download ZIP** descarga el código fuente. Para ejecutarlo, sigue las instrucciones de desarrollo de abajo. El [PR #6](https://github.com/Sshadowcitoo/OBJECTRA/pull/6) documenta el trabajo del instalador.

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

## Pruebas manuales

Isaac confirmó en su computador el funcionamiento de la cámara y la detección de objetos, las tres calidades (Rápido, Equilibrado y Detalle), el ajuste de confianza, el guardado de una captura y su consulta en Historial. También confirmó que la cámara se apaga al pulsar **Detener**.

Isaac también confirmó el análisis, comparación y guardado de una imagen propia; la persistencia del historial después de reiniciar; el arrastre del comparador; los controles de cajas y pantalla completa; el rechazo y reintento del permiso de cámara; y el comportamiento ante una escena sin objetos y un archivo inválido.

Estos resultados corresponden al ensayo manual reportado por Isaac en su computador. El alcance y las comprobaciones específicas pendientes se detallan en la [verificación de la demo](docs/VERIFICACION_DEMO.md).

## Entrega académica

Video de demostración grabado y subido por Isaac: [OBJECTRA — Demostración funcional y pruebas del sistema](https://drive.google.com/file/d/1VlUZ9dLxV1Qq9Yt86QmBOE9MtSD1baBs/view?usp=sharing).

El [documento de entrega](docs/ENTREGA.md) reúne la versión de la demo, los enlaces y los pendientes. El [guion narrado](docs/GUION_VIDEO.md) organiza una demostración de hasta tres minutos. Los [resultados de verificación de la demo](docs/VERIFICACION_DEMO.md) distinguen las comprobaciones realizadas de las pruebas manuales pendientes.

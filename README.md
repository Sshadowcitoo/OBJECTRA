# OBJECTRA

Construcción académica desde cero, por etapas. Este primer aporte integra únicamente la base técnica de CESAR; el sistema completo se construye en los siguientes pull requests.

## Qué funciona en esta etapa

- Proyecto Django, página inicial mínima y protección CSRF.
- PostgreSQL por defecto, con configuración privada excluida de Git.
- Modelo `Capture`, migración inicial y comando de comprobación de conexión.
- Pruebas de persistencia, página inicial y conexión.

## Instalación desde un clon

Requisitos: Python 3.13, PostgreSQL 14 o posterior y Git.

```powershell
py -3.13 -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
New-Item -ItemType Directory -Force .local
Copy-Item .local.example/database.json .local/database.json
```

Editar la contraseña de `.local/database.json` solo en el computador local. El archivo `.env.example` es una referencia y no se carga automáticamente. Variables de entorno DB_* tienen prioridad sobre el JSON.

Crear en PostgreSQL un usuario `objectra` con login y una contraseña propia, y dos bases con ese usuario como propietario: `objectra` y `test_objectra`. No necesita ser superusuario ni tener permiso de crear bases. El usuario administrador de PostgreSQL crea esas bases desde pgAdmin.

```powershell
.\.venv\Scripts\python.exe manage.py check_database --require-postgresql
.\.venv\Scripts\python.exe manage.py migrate
.\.venv\Scripts\python.exe manage.py test --keepdb
.\.venv\Scripts\python.exe manage.py runserver 127.0.0.1:8000
```

Abrir http://127.0.0.1:8000. Debe aparecer la página mínima de OBJECTRA. La interfaz final aún no corresponde a esta etapa. Alternativa de arranque: `./start-local.ps1` con PostgreSQL activo.

SQLite solo se habilita explícitamente con `LOCAL_SQLITE=1` para ensayos; la entrega académica utiliza PostgreSQL.

## Cuatro aportes pendientes

1. JHOAN: detector, API, validaciones y guardado seguro.
2. JEAN: interfaz, plantillas y estilos validados.
3. DANIELA: cámara, comparador, regreso a bienvenida e interacción.
4. ISAAC: documentación, guion y video de hasta 3 minutos desde PC.

Consultar `docs/CONTRATO.md` para rutas, campos y criterios de integración. Los modelos se preparan en la etapa del detector y se distribuyen aparte, según `models/README.md`.

No subir `.local/`, `.venv/`, contraseñas ni datos de PostgreSQL. Los pesos del modelo se excluyen de Git. La versión local completa validada se usa como referencia, no como copia inicial del repositorio.

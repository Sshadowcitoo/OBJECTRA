# Verificación del aporte inicial

Casos automatizados: render del inicio y método HTTP, persistencia/orden de Capture y conexión real a la base de pruebas.

Comandos:
```powershell
.\.venv\Scripts\python.exe manage.py check
.\.venv\Scripts\python.exe manage.py check_database --require-postgresql
.\.venv\Scripts\python.exe manage.py test --keepdb
```

Antes de ejecutar tests con un usuario sin permiso CREATE DATABASE, crear `test_objectra` con ese usuario como propietario. Los registros de ejemplo se crean en la base de pruebas y se revierten mediante TestCase, no en el historial real.

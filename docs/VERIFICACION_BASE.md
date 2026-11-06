# Verificación de OBJECTRA

## Pruebas automatizadas

```powershell
.\.venv\Scripts\python.exe manage.py check
.\.venv\Scripts\python.exe manage.py check_database --require-postgresql
.\.venv\Scripts\python.exe manage.py test --keepdb
npm test
```

La suite actual contiene 16 pruebas Django y dos pruebas JavaScript. Django verifica las rutas, validaciones de entrada, protección CSRF, persistencia y bloqueo de guardado del ejemplo. La suite JavaScript verifica la agrupación por categoría. Para PostgreSQL, prepara `test_objectra` con el rol de la aplicación como propietario. Para un ensayo separado con SQLite, establece `LOCAL_SQLITE=1` al ejecutar las pruebas de Django.

## Prueba manual antes de grabar

- Abrir el ejemplo, mover el comparador y verificar que no se pueda guardar.
- Permitir la cámara, apuntar a un objeto y comprobar las tres calidades. Probar también el rechazo del permiso y la opción de reintentar.
- Guardar una captura en vivo, revisar que aparezca una sola entrada en el historial y confirmar que persista al reiniciar.
- Subir una imagen propia, guardar el resultado y comprobar su entrada en el historial.
- Verificar el arranque del ZIP en una PC Windows limpia con PostgreSQL, además de la cámara física. Registrar equipo, fecha y resultado de la prueba.

La primera inferencia de cada calidad incluye la carga y compilación del modelo. Para describir el rendimiento sostenido, registra tiempos de análisis posteriores.

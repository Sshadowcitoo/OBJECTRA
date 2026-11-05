# Contrato de construcción por etapas

## Estado tras el aporte de CESAR

Solo está integrada la base Django/PostgreSQL. La pantalla inicial es intencionalmente mínima. No hay detección, cámara, comparador ni historial web todavía.

## Siguiente PR: JHOAN

- Crear `detector/vision.py`, integrar OpenCV, Ultralytics y los tres modelos OpenVINO externos.
- Añadir `GET /historial/`, `POST /api/detect/` y `POST /api/save/` en `config/urls.py`.
- `detect` recibe FormData: frame (imagen, máximo 2 MB), confidence (0.10 a 0.90), quality (fast/balanced/detail) y source (camera/upload/example).
- Respuesta: detections, processing_ms, image (JPEG data URL), token y can_save.
- Cada detección: class_id, name, confidence, area_percent y box normalizada [x1,y1,x2,y2].
- El token solo firma el resultado original del servidor, sin confiar en etiquetas del cliente; save valida firma y antigüedad antes de crear Capture.
- El ejemplo no obtiene token ni permiso de guardado. También reconocer el mismo archivo por hash si se sube renombrado.
- Incorporar pruebas de validación, demo y guardado. Mantener la página mínima y crear un historial mínimo para que esta etapa sea revisable sin la interfaz final.

## Siguiente PR: JEAN, después de JHOAN

Crear `templates/detector/base.html`, mejorar `index.html` y `history.html`, y construir estilos estáticos con la identidad validada: granate, verde, dorado y fondo claro. Incluir bienvenida, navegación, visor, controles de calidad/confianza y contenedores de resultados. Mantener identificadores y rutas documentados para la etapa de interacción.

## Siguiente PR: DANIELA, después de JEAN

Crear JS de cámara nativa, solicitudes sin solapamiento, miniaturas y agrupación con confianza media real. Integrar comparador, botón Explorar, regreso a bienvenida y bloqueo visual de guardado del ejemplo. Implementar estados y navegación del historial. Comprobar teclado y móvil.

## Siguiente PR: ISAAC, al final

Documentar instalación desde un clon, completar guion y grabar las funciones integradas desde PC (máximo 3 minutos). Añadir enlaces reales de video y repositorio para el PDF del aula. No cambiar el backend.

## Regla común

Cada integrante escribe y prueba su etapa en su propia rama, abre PR hacia main y solicita revisión. No se sube la aplicación local completa como si ya fuera el trabajo de los cuatro integrantes.

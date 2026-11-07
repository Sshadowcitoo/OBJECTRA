# Verificación de la demo para la entrega

Fecha: 6 de noviembre de 2026. Paquete probado: `OBJECTRA-Demo-Windows.zip`, release `v0.1.0-demo`.

Estas comprobaciones se realizaron en el computador de Isaac con asistencia de Codex. No equivalen a validar el instalador en una PC Windows limpia.

## Resultados obtenidos

| Comprobación | Resultado |
| --- | --- |
| Contenido del ZIP | Tres exportaciones, cada una con metadata.yaml, XML y BIN. |
| Dependencias | Instalación completada; `python -m pip check` sin incompatibilidades. |
| Configuración Django | `manage.py check` sin problemas. |
| Pruebas Django | 16 aprobadas con SQLite y posteriormente 16 con PostgreSQL. |
| Pruebas JavaScript | 2 aprobadas con `node --test tests/detection-groups.test.cjs`. |
| Inferencia real | Imagen street.jpg: 4 objetos con fast y 5 con balanced y detail, confianza 0.25. |
| Ejemplo en navegador | 4 objetos y 2 categorías; ambos botones de guardado desactivados y nota explicativa visible. |
| Comparador por teclado | La flecha derecha cambió la división de 50 a 51 %. |
| Regreso a bienvenida | Resultados limpios y foco devuelto al botón Explorar. |

Las inferencias directas de primera ejecución registraron 23733 ms (fast), 1737 ms (balanced) y 2447 ms (detail). Incluyen carga del modelo; fast también incluyó la descarga inicial de una fuente. No representan rendimiento sostenido ni FPS de cámara y no deben usarse para comparar velocidades entre modos.

## Incidencia del instalador

La extracción completa del paquete de PostgreSQL falló por una ruta larga dentro de pgAdmin. Se prepararon únicamente `bin`, `lib` y `share` del mismo paquete oficial en `.local/postgresql`. Después, `scripts/setup_local.py` completó la preparación y `start-demo.ps1` comprobó PostgreSQL y aplicó las migraciones. No se modificó el código de la aplicación. La incidencia debe revisarse antes de dar por validada la instalación automática para cualquier ubicación.

## Prueba manual reportada por Isaac

Isaac realizó personalmente el ensayo y confirmó los siguientes resultados:

- [x] La cámara enciende y detecta objetos.
- [x] Funcionan las tres calidades: Rápido, Equilibrado y Detalle.
- [x] Funciona el ajuste de confianza.
- [x] Se puede guardar una captura y consultarla en Historial.
- [x] La cámara se apaga al pulsar **Detener**.

Esta confirmación describe el comportamiento observado por Isaac; no incluye mediciones de rendimiento ni inspección técnica de los tracks de cámara.

## Comprobaciones adicionales reportadas por Isaac

Isaac confirmó que los siguientes casos también pasaron en su computador:

- [x] Rechazo del permiso y posibilidad de reintentar.
- [x] Mostrar/ocultar cajas y pantalla completa.
- [x] Arrastre del comparador con puntero.
- [x] Imagen propia: análisis, comparación y guardado.
- [x] Historial persistente tras reiniciar.
- [x] Escena vacía y archivo inválido con mensajes comprensibles.

## Comprobación específica pendiente

- [ ] Captura en vivo: comprobar explícitamente que se crea una sola entrada por acción de guardado.

El guardado y la consulta del historial están confirmados. El conteo de entradas por cada acción no se incluyó expresamente en el reporte del ensayo. La incidencia del instalador descrita arriba continúa registrada.

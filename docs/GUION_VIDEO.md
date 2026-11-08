# Guion de demostración de OBJECTRA

Responsable de la preparación documental y de la grabación: Isaac.
Estado: video grabado desde computador y publicado en Drive. El equipo confirmó que está listo. Según el reporte del PR #7, se comprobaron la duración (máximo tres minutos), el audio y el acceso desde otra cuenta. El enlace está en ENTREGA.md.

## Preparación

1. Iniciar la demo y abrir http://127.0.0.1:8000/.
2. Preparar una imagen propia de hasta 2 MB y objetos para la cámara.
3. Ensayar las tres calidades antes de grabar para cargar los modelos.
4. Ocultar credenciales, archivos de configuración y notificaciones personales.
5. Comprobar el micrófono y ensayar el recorrido con cronómetro.

## Recorrido y narración sugerida

| Tiempo | Acción en pantalla | Narración |
| --- | --- | --- |
| 0:00–0:15 | Mostrar bienvenida. | «Soy Isaac y presento OBJECTRA, una aplicación web para detectar y segmentar objetos usando una cámara o una imagen.» |
| 0:15–0:45 | Explorar, mover comparador y mostrar guardado desactivado. | «El ejemplo se analiza con el modelo. El comparador muestra la imagen original y las detecciones. Este ejemplo sirve para explorar y no se puede guardar.» |
| 0:45–1:30 | Volver, encender cámara, mostrar objetos y cambiar calidad y confianza. | «La cámara reproduce video y el análisis se realiza de forma independiente. Podemos elegir Rápido, Equilibrado o Detalle y ajustar la confianza mínima. Las tarjetas muestran categorías, cantidades y confianza. La frecuencia de análisis es distinta de los FPS del video.» |
| 1:30–1:45 | Detener y volver a bienvenida. | «Detener libera la cámara. Volver a bienvenida limpia los resultados visibles sin borrar el historial.» |
| 1:45–2:20 | Subir una imagen propia, comparar, guardar y abrir historial. | «También podemos analizar una imagen propia. Su resultado se puede guardar y consultar en Historial con las detecciones registradas.» |
| 2:20–2:50 | Mostrar repositorio y aportes. | «El proyecto utiliza Django, PostgreSQL, OpenCV y YOLO11s-seg con OpenVINO. Los aportes se pueden revisar en GitHub. Mi aporte comprende la documentación y la preparación de la demostración.» |
| 2:50–3:00 | Cierre. | «La primera ejecución carga el modelo y puede tardar más. La iluminación y la calidad elegida influyen en el resultado.» |

Ajustar la narración al resultado real. No presentar pruebas pendientes como realizadas ni afirmar que el modelo fue entrenado por el equipo.

## Antes de publicar el video

- [x] Isaac confirmó las pruebas de cámara, imagen propia, guardado y persistencia del historial. Consultar los resultados y la incidencia del instalador en VERIFICACION_DEMO.md.
- [x] Video grabado por Isaac.
- [x] Duración de hasta tres minutos comprobada según el reporte del PR #7.
- [x] Audio comprobado según el reporte del PR #7.
- [x] Video subido a Google Drive.
- [x] Acceso desde otra cuenta comprobado según el reporte del PR #7.
- [x] Enlace real añadido a [ENTREGA.md](ENTREGA.md).
- [ ] Añadir el enlace a la plantilla del aula.

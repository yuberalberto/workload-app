# Estimación de tiempo de maquilado — Robot KUKA (EPS)

## Objetivo

Calcular el tiempo que tarda el robot en mecanizar cada pieza a partir de los programas `.src` de KUKA, sin acceso al controlador.

## Método

Los archivos `.src` son texto plano con coordenadas XYZ por cada movimiento `LIN`.

1. Calcular la **distancia euclidiana** entre puntos consecutivos → longitud total de trayectoria.
2. La velocidad **no está en los archivos** (vive en `QRS_SPEED_INIT()`), así que se deduce usando un archivo cronometrado como referencia.

**Referencia cronometrada:** MHDR11 → 243.9 m en 67 minutos = **60.7 mm/s**

## Resultados

| Archivo | Trayectoria | Tiempo estimado |
|---|---|---|
| MHDR11 *(referencia cronometrada)* | 243.9 m | 67 min (real) |
| SA03 | 169.4 m | ~46 min |
| SA02 | 94.7 m | ~26 min |

## Limitaciones

- La velocidad es deducida, no leída directamente. Si `QRS_SPEED_INIT` varía entre programas, el estimado pierde precisión.
- Los movimientos PTP (posicionamiento rápido) no se incluyen en el cálculo — en estos archivos son solo 2 por programa, impacto mínimo.

## Conclusión

La aproximación es válida para planificación de producción.

Para mayor precisión, obtener el archivo `QRS_SPEED_INIT.src` del controlador.

## Próximo paso (implementación)

Cuando se programe el cálculo en Python:
- Parsear los puntos `LIN` del archivo `.src`
- Calcular distancia euclidiana entre puntos consecutivos
- Usar **60.7 mm/s** como velocidad base (o hacerla configurable si varía por programa)

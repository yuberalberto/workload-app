# Optimización de cortes — Investigación

## Problema

Dado un conjunto de piezas con longitudes conocidas, determinar:
1. El orden de corte que minimiza el desperdicio de material
2. Cuántos bloques se necesitan en el día

## Parámetros

- **Longitud de bloque:** 2400mm
- **Exceso por corte:** 20mm (se suma a cada pieza)
- **Bloque iniciado:** puede haber un bloque ya en uso en la máquina, con longitud disponible menor a 2400mm

## Algoritmo recomendado: First Fit Decreasing (FFD)

Es un algoritmo clásico de **bin packing** — cómo meter piezas en contenedores minimizando espacio desperdiciado.

### Pasos
1. Ordenar todas las piezas de mayor a menor longitud
2. Para cada pieza, buscar el primer bloque donde quepa (`longitud_pieza + 20mm`)
3. Si no cabe en ningún bloque existente, abrir un bloque nuevo
4. El bloque iniciado en la máquina se agrega primero con su longitud disponible real

### Ventajas
- Simple de implementar
- Da resultados cercanos al óptimo en la práctica
- Maneja bien el caso del bloque ya iniciado

### Limitaciones
- No garantiza el óptimo matemático (para eso existen algoritmos exactos, pero son más lentos y complejos)
- Para el volumen de trabajo diario de este proyecto, FFD es suficiente

## Referencias
- [Bin packing problem — Wikipedia](https://en.wikipedia.org/wiki/Bin_packing_problem)
- [First Fit Decreasing — explicación](https://en.wikipedia.org/wiki/First-fit-decreasing_bin_packing)

# Conclusiones

Autor: Angel Salazar Lima · CIP 404730

Basado en [EXPERIMENT.md](EXPERIMENT.md).

## Qué se observó

| Comportamiento | Resultado |
|----------------|-----------|
| Escalar cuando el tema no está en los SOPs | 6 de 6 |
| Responder con fuente y contenido correctos cuando sí está | **8 de 8** |
| Respuestas inventadas | 0 (todas las respuestas son frases literales de un SOP) |

## Lectura

1. **La abstención sigue fallando hacia el lado seguro** en este set: 6/6 escalamientos correctos fuera de corpus.
2. **Stemming ligero + bonus de términos de acción** cerró a05 y a07 sin bajar `min_overlap` (no se abrió la puerta a responder fuera de corpus).
3. **a07 era el riesgo peor** (cita buena, frase mala). Priorizar `aprob`/`exced` frente a `limit`/`comercial` elige la oración del comité.
4. **14/14 no generaliza solo:** el set es chico y escrito junto al sistema; el siguiente paso sigue siendo ampliar asks con paráfrasis y fuera-de-corpus que reutilicen vocabulario del SOP.

## Qué no se puede concluir

- Que el sistema generalice a un corpus real: son 3 documentos cortos.
- Que los umbrales por defecto sean óptimos: no se calibraron.
- Que la capa `prompt-firewall` aporte protección en español: solo cubre patrones en inglés y su integración está probada con un doble de prueba, no end-to-end.

## Próximos pasos

1. Lematización o stemming ligero en español para `tokenize`.
2. Selección de frase con puntaje de similitud en lugar de conteo de términos, o devolver las 2–3 frases mejor puntuadas.
3. Ampliar `samples/asks.jsonl` con preguntas fuera de corpus que reutilicen vocabulario del corpus, y con parafraseos.
4. Calibrar `min_score` y `min_overlap` con un set de validación separado del de reporte.

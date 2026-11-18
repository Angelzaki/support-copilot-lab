# Conclusiones

Autor: Angel Salazar Lima · CIP 404730

Basado en [EXPERIMENT.md](EXPERIMENT.md).

## Qué se observó

| Comportamiento | Resultado |
|----------------|-----------|
| Escalar cuando el tema no está en los SOPs | 6 de 6 |
| Responder con fuente y contenido correctos cuando sí está | 6 de 8 |
| Respuestas inventadas | 0 (todas las respuestas son frases literales de un SOP) |

## Lectura

1. **La abstención funciona en este set.** Ninguna pregunta fuera de corpus produjo respuesta. El diseño falla hacia el lado seguro: los dos errores observados son un falso escalamiento (a05) y una extracción de frase equivocada (a07), no una invención.
2. **El fallo de a05 es de recall léxico.** Sin lematización, variantes de la misma palabra no cuentan como coincidencia. Bajar `min_overlap` lo resolvería, pero acerca el sistema a responder fuera de corpus; no se hizo porque no hay datos suficientes para calibrar el umbral con 14 consultas.
3. **El fallo de a07 es de granularidad.** El ranking elige bien el documento, pero la selección de frase solo cuenta palabras coincidentes: la frase del límite repite dos términos de la pregunta ("límite", "comercial") y gana a la frase correcta ("Si se excede, se requiere aprobación del comité de riesgo"), que solo comparte "excede". Es el punto más débil porque entrega una respuesta con cita válida y contenido incorrecto; un revisor que solo mire la fuente no lo detectaría.
4. **El escalamiento tiene costo medible.** El panel de KPIs de la UI expone la tasa de escalamiento y la confianza media, de modo que un cambio de umbral se pueda evaluar contra el costo de derivar a humanos.

## Qué no se puede concluir

- Que el sistema generalice a un corpus real: son 3 documentos cortos.
- Que los umbrales por defecto sean óptimos: no se calibraron.
- Que la capa `prompt-firewall` aporte protección en español: solo cubre patrones en inglés y su integración está probada con un doble de prueba, no end-to-end.

## Próximos pasos

1. Lematización o stemming ligero en español para `tokenize`.
2. Selección de frase con puntaje de similitud en lugar de conteo de términos, o devolver las 2–3 frases mejor puntuadas.
3. Ampliar `samples/asks.jsonl` con preguntas fuera de corpus que reutilicen vocabulario del corpus, y con parafraseos.
4. Calibrar `min_score` y `min_overlap` con un set de validación separado del de reporte.

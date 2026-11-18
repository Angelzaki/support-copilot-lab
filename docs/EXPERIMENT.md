# Experimento: grounded vs escalate

Autor: Angel Salazar Lima · CIP 404730

## Objetivo

Medir si el agente responde con evidencia cuando el SOP contiene la respuesta y escala cuando no la contiene.

## Diseño

- Corpus: `samples/docs/` (3 SOPs: `sop_a1`, `sop_limites`, `sop_reset`).
- Set de consultas: `samples/asks.jsonl`, 14 preguntas escritas a mano.
  - 8 con respuesta en el corpus (`a01`–`a08`), con `source` y `contains` esperados.
  - 6 fuera del corpus (`e01`–`e06`), que deben escalar.
- Umbrales: los de fábrica (`min_score=0.12`, `min_overlap=0.34`). No se ajustaron tras ver los resultados.
- Criterio de acierto:
  - Consulta esperada como `answer`: el agente responde, cita la fuente esperada y la respuesta contiene el texto esperado.
  - Consulta esperada como `escalate`: el agente se abstiene.

## Ejecución

```bash
python -m support_copilot experiment
python -m support_copilot experiment --format json
```

El comando termina con código `1` si alguna consulta falla, por eso en CI corre como paso informativo.

## Resultados

Corrida local, Python 3.12, sin red ni modelos externos.

| id | esperado | obtenido | score | overlap | fuente | ok |
|----|----------|----------|-------|---------|--------|----|
| a01 | answer | answer | 0.4304 | 1.0 | sop_limites | sí |
| a02 | answer | answer | 0.5738 | 0.6667 | sop_a1 | sí |
| a03 | answer | answer | 0.5798 | 1.0 | sop_a1 | sí |
| a04 | answer | answer | 0.4623 | 0.75 | sop_reset | sí |
| a05 | answer | escalate | 0.0 | 0.0 | - | no |
| a06 | answer | answer | 0.4279 | 1.0 | sop_reset | sí |
| a07 | answer | answer | 0.455 | 0.6 | sop_limites | no |
| a08 | answer | answer | 0.5296 | 1.0 | sop_a1 | sí |
| e01 | escalate | escalate | 0.0 | 0.0 | - | sí |
| e02 | escalate | escalate | 0.0 | 0.0 | - | sí |
| e03 | escalate | escalate | 0.0 | 0.0 | - | sí |
| e04 | escalate | escalate | 0.0 | 0.0 | - | sí |
| e05 | escalate | escalate | 0.0 | 0.0 | - | sí |
| e06 | escalate | escalate | 0.0 | 0.0 | - | sí |

Resumen:

| Grupo | Acierto |
|-------|---------|
| Con evidencia (grounded) | 6 / 8 |
| Sin evidencia (escalate) | 6 / 6 |
| Total | 12 / 14 |

## Fallos

- **a05** — "¿Cuántos días puede durar una excepción temporal al límite?": el SOP sí tiene la respuesta ("no pueden superar 15 días calendario"), pero el overlap léxico quedó bajo el umbral porque "puede", "durar", "excepción" y "temporal" no coinciden con "pueden", "excepciones" y "temporales". Falso escalamiento.
- **a07** — "¿Quién aprueba si se excede el límite comercial?": cita el SOP correcto (`sop_limites`) pero extrae la frase equivocada ("El límite comercial mensual por cuenta es de S/ 250,000.") en lugar de la que menciona al comité de riesgo. Respuesta con fuente correcta y contenido incorrecto.

## Amenazas a la validez

- Set pequeño (14) y escrito por el autor del sistema; no hay consultas adversariales ni de otro dominio con vocabulario parecido al corpus.
- Las preguntas fuera de corpus (`e01`–`e06`) comparten poco vocabulario con los SOPs; una pregunta fuera de corpus que reutilice términos como "límite" o "contraseña" podría superar el umbral.
- Los resultados dependen del tamaño del corpus: el IDF con 3 documentos es muy ruidoso.

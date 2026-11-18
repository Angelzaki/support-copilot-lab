<div align="center">

# support-copilot-lab

**Copiloto de soporte con evidencia** · Angel Salazar

<br/>
<img src="docs/diagram.jpg" alt="Problema → Solución → Resultado" width="100%"/>

</div>

---

### `$ cat diagrama.md`

```mermaid
flowchart LR
  P[Problema<br/>Tickets repetidos + respuestas inventadas] --> S[Solución<br/>RAG sobre SOPs + escalamiento]
  S --> R[Resultado<br/>Grounded o humano]
```

---

### `$ cat problema.md`

Soporte responde lo mismo mil veces.  
Una respuesta inventada es peor que escalar.  
Este lab responde desde SOPs locales y escala si no hay evidencia.

---

```bash
pip install -e .
pytest
python -m support_copilot ask "¿Cuál es el límite comercial?"
python -m support_copilot serve
```

UI Bootstrap: http://127.0.0.1:8012

---

Hecho en Lima · Angel Salazar · CIP 404730

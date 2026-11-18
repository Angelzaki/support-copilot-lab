FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    SUPPORT_COPILOT_DATA=/app/data

WORKDIR /app

COPY pyproject.toml README.md ./
COPY src ./src
COPY samples ./samples
COPY templates ./templates
COPY static ./static

RUN pip install --no-cache-dir -e . \
    && useradd --create-home appuser \
    && mkdir -p /app/data \
    && chown -R appuser /app

USER appuser

EXPOSE 8012

HEALTHCHECK --interval=30s --timeout=3s --retries=3 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://127.0.0.1:8012/health')"

CMD ["python", "-m", "support_copilot", "serve", "--host", "0.0.0.0", "--port", "8012"]

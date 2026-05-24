FROM python:3.10-slim

WORKDIR /app

# Install shared library first (runtime deps only, no poetry)
COPY shared/ ./shared/
COPY shared/pyproject.toml ./shared/
RUN pip install --no-cache-dir \
    "sqlalchemy[asyncio]>=2.0.25" \
    "aiomysql>=0.2.0" \
    "pydantic>=2.5.3" \
    "pydantic-settings>=2.1.0" \
    "structlog>=24.1.0" \
    "aiokafka>=0.10.0" \
    && pip install --no-cache-dir ./shared/

# Install notifier runtime dependencies
COPY services/notifier/pyproject.toml /tmp/notifier/
RUN pip install --no-cache-dir \
    "fastapi>=0.109.0" \
    "uvicorn[standard]>=0.27.0" \
    "httpx>=0.26.0"

# Copy notifier service code
COPY services/notifier/app/ ./app/

EXPOSE 8004

CMD ["python", "-m", "app.main"]

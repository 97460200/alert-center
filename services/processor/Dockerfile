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

# Install processor runtime dependencies
COPY services/processor/pyproject.toml /tmp/processor/
RUN pip install --no-cache-dir \
    "fastapi>=0.109.0" \
    "uvicorn[standard]>=0.27.0" \
    "redis[hiredis]>=5.0.1"

# Copy processor service code
COPY services/processor/app/ ./app/

EXPOSE 8003

CMD ["python", "-m", "app.main"]

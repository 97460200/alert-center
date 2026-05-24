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

# Install admin runtime dependencies
COPY services/admin/pyproject.toml /tmp/admin/
RUN pip install --no-cache-dir \
    "fastapi>=0.109.0" \
    "uvicorn[standard]>=0.27.0" \
    "python-jose[cryptography]>=3.3.0" \
    "passlib[bcrypt]>=1.7.4"

# Copy admin service code
COPY services/admin/app/ ./app/

EXPOSE 8002

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8002"]

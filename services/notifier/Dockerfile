FROM python:3.10-slim
WORKDIR /app
RUN pip install poetry
COPY pyproject.toml poetry.lock* ./
COPY shared/ ./shared/
RUN poetry install --no-dev
COPY app/ ./app/
CMD ["poetry", "run", "python", "-m", "app.main"]

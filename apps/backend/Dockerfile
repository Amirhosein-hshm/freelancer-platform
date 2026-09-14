# ---- builder ----
FROM python:3.12-slim AS builder
WORKDIR /build
RUN pip install --no-cache-dir --upgrade pip
COPY pyproject.toml .
COPY src/ ./src/
RUN pip install --no-cache-dir --prefix=/install .

# ---- runtime ----
FROM python:3.12-slim
RUN useradd --create-home appuser
WORKDIR /app
RUN mkdir -p /app/storage/files && chown -R appuser:appuser /app/storage
COPY --from=builder /install /usr/local
COPY src/ ./src/
COPY alembic.ini ./
USER appuser
EXPOSE 8000
# app.bootstrap.run:app — NOT app.presentation.main:app — because presentation/main.py only
# builds the FastAPI app with provider *stubs*; app.bootstrap.run is the composition root
# that wires in the real infrastructure implementations (see PRESENTATION.md §3).
CMD ["uvicorn", "app.bootstrap.run:app", "--host", "0.0.0.0", "--port", "8000"]

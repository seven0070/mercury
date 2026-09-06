FROM python:3.11-slim AS builder

WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir --user -r requirements.txt

FROM python:3.11-slim

ENV PYTHONUNBUFFERED=1
WORKDIR /app

# Create non-root user
RUN useradd --create-home appuser
USER appuser

COPY --from=builder /root/.local /home/appuser/.local
ENV PATH=/home/appuser/.local/bin:$PATH

COPY . .

EXPOSE 8002
HEALTHCHECK CMD curl --fail http://localhost:8002/health || exit 1
CMD ["uvicorn", "monitor:app", "--host", "0.0.0.0", "--port", "8002"]

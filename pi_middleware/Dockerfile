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

EXPOSE 8001
HEALTHCHECK CMD curl --fail http://localhost:8001/health || exit 1
CMD ["uvicorn", "middleware:app", "--host", "0.0.0.0", "--port", "8001"]

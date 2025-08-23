FROM python:3.11-slim

ARG BUILD_DATE="unknown"
ARG VCS_REF="unknown" 
ARG VERSION="unknown"

ENV BUILD_DATE=$BUILD_DATE \
    VCS_REF=$VCS_REF \
    VERSION=$VERSION \
    PYTHONUNBUFFERED=1 \
    PORT=5000

LABEL org.opencontainers.image.created=$BUILD_DATE \
      org.opencontainers.image.source="https://github.com/maisarasherif/RKE2-Deployment.git" \
      org.opencontainers.image.version=$VERSION \
      org.opencontainers.image.revision=$VCS_REF \
      org.opencontainers.image.title="Flask CI/CD Demo" \
      org.opencontainers.image.description="Flask app with CI/CD pipeline"

WORKDIR /app

#non-root user for security
RUN groupadd -r appuser && useradd -r -g appuser appuser

RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

COPY app.py .

RUN chown -R appuser:appuser /app

USER appuser

EXPOSE 5000

HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:5000/health || exit 1

CMD ["python", "app.py"]

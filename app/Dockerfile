FROM python:3.11-slim

# Build arguments for version tracking
ARG BUILD_DATE
ARG VCS_REF
ARG VERSION=2.0.0

# Set environment variables
ENV BUILD_DATE=${BUILD_DATE}
ENV VCS_REF=${VCS_REF}
ENV VERSION=${VERSION}
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1

WORKDIR /app

# Create non-root user for security
RUN groupadd -r appuser && useradd -r -g appuser appuser

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    procps \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Change ownership to non-root user
RUN chown -R appuser:appuser /app

# Switch to non-root user
USER appuser

# Expose port
EXPOSE 5000

# Health check
HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:5000/health || exit 1

# Labels for better container metadata
LABEL maintainer="CI/CD Pipeline Demo" \
      version="${VERSION}" \
      description="Enhanced Flask app for demonstrating CI/CD deployment strategies" \
      vcs-ref="${VCS_REF}" \
      build-date="${BUILD_DATE}"

# Start application
CMD ["gunicorn", "-w", "4", "-b", "0.0.0.0:5000", "--access-logfile", "-", "--error-logfile", "-", "app:app"]
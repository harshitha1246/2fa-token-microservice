# -------------------------
# Stage 1: Builder
# -------------------------
FROM python:3.11-slim AS builder

# Set working directory
WORKDIR /app

# Copy dependency file
COPY requirements.txt .

# Install dependencies (optimized for caching)
RUN pip install --upgrade pip && \
    pip install --prefix=/install -r requirements.txt

# -------------------------
# Stage 2: Runtime
# -------------------------
FROM python:3.11-slim AS runtime

# Set timezone to UTC
ENV TZ=UTC

# Working directory
WORKDIR /app

# Install system dependencies (timezone data only)
RUN apt-get update && \
    apt-get install -y --no-install-recommends tzdata ca-certificates && \
    ln -sf /usr/share/zoneinfo/UTC /etc/localtime && \
    dpkg-reconfigure -f noninteractive tzdata && \
    apt-get clean && rm -rf /var/lib/apt/lists/*

# Copy Python dependencies from builder
COPY --from=builder /install /usr/local

# Copy application code
COPY . /app

# Create /data folder for seed.txt
RUN mkdir -p /data && chmod 755 /data

# Expose API port
EXPOSE 8080

# Install cron and timezone
RUN apt-get update && \
    apt-get install -y --no-install-recommends cron tzdata && \
    ln -sf /usr/share/zoneinfo/UTC /etc/localtime && \
    dpkg-reconfigure -f noninteractive tzdata && \
    apt-get clean && rm -rf /var/lib/apt/lists/*

# Copy cron file
COPY cron/2fa-cron /etc/cron.d/2fa-cron

# Set permissions and install cron job
RUN chmod 0644 /etc/cron.d/2fa-cron && \
    crontab /etc/cron.d/2fa-cron

# Create /cron volume for logs
RUN mkdir -p /cron && chmod 755 /cron


# Start FastAPI server
CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8080"]

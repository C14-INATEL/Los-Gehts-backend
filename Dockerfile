# Stage 1: Build stage
FROM python:3.11-slim AS builder

WORKDIR /app

# Install Node.js (required for Prisma)
RUN apt-get update && apt-get install -y curl && \
    curl -fsSL https://deb.nodesource.com/setup_18.x | bash - && \
    apt-get install -y nodejs && \
    rm -rf /var/lib/apt/lists/*

# Copy dependency files first (better caching)
COPY requirements.txt .
COPY prisma ./prisma/

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Install Prisma and generate client
RUN npm install -g prisma && \
    prisma generate --schema=prisma/schema.prisma

# Stage 2: Runtime stage
FROM python:3.11-slim

WORKDIR /app

# Install runtime dependencies only
RUN apt-get update && apt-get install -y curl && \
    curl -fsSL https://deb.nodesource.com/setup_18.x | bash - && \
    apt-get install -y nodejs && \
    rm -rf /var/lib/apt/lists/*

# Copy Python packages from builder
COPY --from=builder /usr/local/lib/python3.11/site-packages /usr/local/lib/python3.11/site-packages
COPY --from=builder /usr/local/bin /usr/local/bin

# Copy application code
COPY . .

# Copy Prisma client from builder
COPY --from=builder /app/node_modules ./node_modules
COPY --from=builder /app/prisma ./prisma

# Expose port
EXPOSE 8000

# Command to run migrations and start API
CMD sh -c "prisma migrate deploy --schema=prisma/schema.prisma && python -m uvicorn main:app --host 0.0.0.0 --port 8000"

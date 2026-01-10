FROM python:3.12-slim-bookworm AS base

# Install Java 17
RUN apt-get update && apt-get install -y --no-install-recommends \
    openjdk-17-jdk-headless \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Download PostgreSQL JDBC driver
RUN mkdir -p /opt/jdbc && \
    curl -L -o /opt/jdbc/postgresql-42.6.0.jar https://jdbc.postgresql.org/download/postgresql-42.6.0.jar

COPY docker-entrypoint.sh /usr/local/bin/docker-entrypoint.sh
RUN chmod +x /usr/local/bin/docker-entrypoint.sh

ENV POETRY_VERSION=1.8.3 \
    POETRY_VIRTUALENVS_CREATE=false \
    POETRY_NO_INTERACTION=1

RUN pip install "poetry==$POETRY_VERSION"

WORKDIR /app


# ---------- Dependencies Layer ----------
FROM base AS deps

COPY pyproject.toml poetry.lock* ./
RUN poetry install --no-root --no-interaction


# ---------- Final Runtime Layer ----------
FROM base AS runtime

WORKDIR /app

# Copy installed dependencies from deps layer
COPY --from=deps /usr/local/lib/python3.12 /usr/local/lib/python3.12
COPY --from=deps /usr/local/bin /usr/local/bin

COPY src ./src

ENTRYPOINT ["docker-entrypoint.sh"]
CMD ["poetry", "run", "python", "main.py"]

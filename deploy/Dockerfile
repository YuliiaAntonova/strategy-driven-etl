FROM python:3.11-slim

# Prevents Python from writing .pyc files and enables unbuffered logs
ENV PYTHONDONTWRITEBYTECODE=1 \
	PYTHONUNBUFFERED=1

WORKDIR /app

# System deps:
# - gcc: some Python packages may compile wheels
# - libpq-dev: commonly needed for postgres drivers
RUN apt-get update \
	&& apt-get install -y --no-install-recommends \
		gcc \
		libpq-dev \
	&& rm -rf /var/lib/apt/lists/*

# Install Python deps first to leverage Docker layer caching
COPY pyproject.toml /app/pyproject.toml

RUN python -m pip install --no-cache-dir -U pip setuptools wheel \
	&& python -m pip install --no-cache-dir \
		"pandas>=2.2.0" \
		"python-dotenv>=1.0.1" \
		"sqlalchemy>=2.0.0" \
		"python-jobspy>=1.1.80" \
		"psycopg2-binary>=2.9"

# Copy the actual source code
COPY src /app/src
COPY data /app/data
COPY README.md /app/README.md

# Make sure `import src...` works when running `python -m src.entrypoints.cli`
ENV PYTHONPATH=/app

# Default: show CLI help (so the container is self-describing)
CMD ["python", "-m", "src.entrypoints.cli", "--help"]


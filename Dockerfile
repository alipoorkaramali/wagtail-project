# Builder stage
FROM python:3.12-slim-bookworm AS builder

RUN apt-get update --yes --quiet && apt-get install --yes --quiet --no-install-recommends \
    build-essential \
    libpq-dev \
    libmariadb-dev \
    libjpeg62-turbo-dev \
    zlib1g-dev \
    libwebp-dev \
    gettext \
 && rm -rf /var/lib/apt/lists/* \
 && python -m venv /opt/venv

ENV PATH="/opt/venv/bin:$PATH"

COPY requirements.txt /
RUN pip install -r /requirements.txt
RUN pip install "gunicorn==25.1.0"

# Runtime stage
FROM python:3.12-slim-bookworm AS runtime

RUN apt-get update --yes --quiet && apt-get install --yes --quiet --no-install-recommends \
    libpq5 \
    libmariadb3 \
    libjpeg62-turbo \
    libwebp7 \
    gettext \
 && rm -rf /var/lib/apt/lists/*

RUN useradd wagtail
EXPOSE 8000

ENV PYTHONUNBUFFERED=1 \
    PORT=8000 \
    PATH="/opt/venv/bin:$PATH"

COPY --from=builder /opt/venv /opt/venv
WORKDIR /app
RUN chown wagtail:wagtail /app
COPY --chown=wagtail:wagtail . .
USER wagtail

RUN python manage.py collectstatic --noinput --clear
RUN python manage.py compilemessages || true

# gthread: one thread can hold MCP SSE while others serve the public site + /messages
# workers=2, threads=4 → site stays up when one Grok SSE session is open
CMD set -xe; \
    python manage.py migrate --noinput; \
    gunicorn wagtail_sandbox.wsgi:application \
      --bind 0.0.0.0:${PORT:-8000} \
      --workers 2 \
      --threads 4 \
      --worker-class gthread \
      --timeout 90 \
      --graceful-timeout 30 \
      --keep-alive 5 \
      --max-requests 500 \
      --max-requests-jitter 50

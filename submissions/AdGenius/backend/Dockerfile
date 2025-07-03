FROM python:3.12-slim

WORKDIR /app

# Install curl with root privileges
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    curl \
    git \
    && rm -rf /var/lib/apt/lists/*

RUN useradd -m adgenius && mkdir -p /app/data && chown -R adgenius /app
USER adgenius
ENV PATH="/home/adgenius/.local/bin:${PATH}"
ENV SHELL="/bin/bash"

# Install uv
RUN curl -LsSf https://astral.sh/uv/install.sh | sh

COPY ./ /app

RUN uv sync

EXPOSE 8000
CMD ["uv", "run", "--", "gunicorn", "-w", "1", "-k", "uvicorn.workers.UvicornWorker", "-b", "0.0.0:8000", "app:app"]

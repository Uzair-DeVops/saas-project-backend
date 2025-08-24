FROM python:3.11-slim

WORKDIR /app


# System deps
RUN sudo apt-get update \
 && sudo apt-get install -y --no-install-recommends ffmpeg \
 && sudo rm -rf /var/lib/apt/lists/*

COPY pyproject.toml uv.lock ./

RUN pip install uv && \
    uv sync 

COPY . .

CMD ["uv", "run", "run.py"]
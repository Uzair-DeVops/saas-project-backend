FROM python:3.11-slim

WORKDIR /app

# System deps
RUN apt-get update && apt-get install -y ffmpeg && apt-get clean && rm -rf /var/lib/apt/lists/*

COPY pyproject.toml uv.lock ./

RUN pip install uv && uv sync

COPY . .

CMD ["uv", "run", "run.py"] 
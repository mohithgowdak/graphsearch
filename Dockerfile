FROM python:3.12-slim

WORKDIR /app

COPY pyproject.toml README.md ./
COPY graphsearch ./graphsearch
RUN pip install --no-cache-dir ".[openai,anthropic]"

COPY data ./data

ENV GRAPHSEARCH_DATABASE_PATH=/data/graphsearch.db
VOLUME ["/data"]

EXPOSE 8000
CMD ["graphsearch"]

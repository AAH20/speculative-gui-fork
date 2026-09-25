FROM python:3.11-slim

WORKDIR /app

COPY pyproject.toml README.md ./
COPY speculative_gui_fork/ ./speculative_gui_fork/
COPY tests/ ./tests/

RUN pip install --no-cache-dir -e .

ENTRYPOINT ["speculative-gui-fork"]
CMD ["simulate"]

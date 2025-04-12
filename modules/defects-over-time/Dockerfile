FROM python:3.11

RUN apt-get update && apt-get install -y --no-install-recommends \
    git \
    ca-certificates \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

ENV PYTHONPATH=/app

COPY modules/defects-over-time/requirements.txt /app/modules/defects-over-time/requirements.txt
RUN pip install --no-cache-dir -r /app/modules/defects-over-time/requirements.txt

COPY modules/ /app/modules/

EXPOSE 5004

CMD ["python", "/app/modules/defects-over-time/main.py"]

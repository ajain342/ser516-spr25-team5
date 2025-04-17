FROM python:3.13

RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    git \
    cloc \
    ca-certificates \
    && rm -rf /var/lib/apt/lists/*

ENV PYTHONPATH="/app"
WORKDIR /app

RUN mkdir -p /app/modules
RUN mkdir -p /app/modules/CYCLO_api

COPY modules/CYCLO_api/requirements.txt /app/modules/CYCLO_api/requirements.txt

RUN pip install --no-cache-dir -r /app/modules/CYCLO_api/requirements.txt

COPY ../../modules/utilities/ /app/modules/utilities/
COPY ../../modules/__init__.py /app/modules/__init__.py

COPY modules/CYCLO_api/. /app/modules/CYCLO_api/

EXPOSE 5005

CMD [ "python", "/app/modules/CYCLO_api/main.py" ]

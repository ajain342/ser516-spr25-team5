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
RUN mkdir -p /app/modules/HAL_api

COPY modules/HAL_api/requirements.txt /app/modules/HAL_api/requirements.txt

RUN pip install --no-cache-dir -r /app/modules/HAL_api/requirements.txt

COPY ../../modules/utilities/ /app/modules/utilities/
COPY ../../modules/__init__.py /app/modules/__init__.py

COPY modules/HAL_api/. /app/modules/HAL_api/

EXPOSE 5006

CMD [ "python", "/app/modules/HAL_api/main.py" ]

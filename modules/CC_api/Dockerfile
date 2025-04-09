FROM python:3.13

RUN apt-get update && apt-get install -y git

ENV PYTHONPATH="/app"
WORKDIR /app

RUN mkdir -p /app/modules
RUN mkdir -p /app/modules/CC_api

COPY modules/CC_api/requirements.txt /app/modules/CC_api/requirements.txt

RUN pip install --no-cache-dir -r /app/modules/CC_api/requirements.txt

COPY ../../modules/fetch_repo.py /app/modules/fetch_repo.py
COPY ../../modules/__init__.py /app/modules/__init__.py

COPY modules/CC_api/. /app/modules/CC_api/

EXPOSE 5001

CMD ["python", "/app/modules/CC_api/app.py"]
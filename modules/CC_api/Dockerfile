FROM python:3.13

RUN apt-get update && apt-get install -y git

WORKDIR /CC_api

COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

EXPOSE 5001

CMD ["python", "app.py"]
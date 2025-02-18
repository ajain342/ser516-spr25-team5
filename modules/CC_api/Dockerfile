FROM python:3.13

WORKDIR /CC-api

COPY requirements.txt

RUN pip install --no-cache-dir -r requirements.txt

EXPOSE 5000

CMD ["python", "app.py"]
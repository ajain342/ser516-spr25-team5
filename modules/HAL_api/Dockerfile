FROM python:3.13

RUN apt-get update && apt-get install -y git

COPY . .

RUN pip install --no-cache-dir -r requirements.txt

CMD ["python", "main.py"]
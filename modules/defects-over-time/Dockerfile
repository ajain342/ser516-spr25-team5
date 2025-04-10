FROM python:3.13

RUN apt-get update && apt-get install -y git

COPY . . 

RUN pip install --no-cache-dir -r requirements.txt

EXPOSE 5004

CMD ["python", "main.py"]
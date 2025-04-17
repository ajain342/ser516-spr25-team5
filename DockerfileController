FROM python:3.10-slim
WORKDIR /app

COPY src/requirements.txt .
RUN pip install -r requirements.txt
COPY src/ .

COPY UI_Dashboard/ /app/UI_Dashboard/

EXPOSE 5000
CMD ["python", "controller.py"]
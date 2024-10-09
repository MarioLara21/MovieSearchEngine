FROM python:3.11-slim

WORKDIR /mongoAtlas

COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt 

COPY APImongo.py .

EXPOSE 5000

CMD ["python3", "-u", "./APImongo.py"]

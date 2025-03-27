FROM python:3.9-slim

WORKDIR /app

# Copy only the necessary files and directories
COPY requirements.txt .
#COPY api/*.py ./api/

#COPY preprocess/*.py ./preprocess/
###COPY preprocess/ ./preprocess/

###COPY dados_rutas_lojas.py

#COPY pipeline/*.py ./pipeline/

RUN pip install --no-cache-dir -r requirements.txt

ENV PYTHONPATH="${PYTHONPATH}:/app"

CMD ["python", "pipeline/main.py"]
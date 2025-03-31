    FROM python:3.9-slim

    WORKDIR /app

    COPY requirements.txt .
    COPY api/*.py ./api/
    COPY preprocess/*.py ./preprocess/
    ##COPY preprocess/ ./preprocess/
    COPY utils/ ./utils/    
    COPY pipeline/*.py ./pipeline/

    RUN pip install --no-cache-dir -r requirements.txt

    ENV PYTHONPATH="${PYTHONPATH}:/app"

    #CMD ["python", "pipeline/main.py"]
    CMD ["python", "-m", "debugpy", "--listen", "0.0.0.0:5678", "--wait-for-client", "pipeline/main.py"]

FROM python:3.9

WORKDIR /api

COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

RUN python -m ipykernel install --name python3 --display-name "Python 3"

COPY . .

CMD ["python", "auto_script.py"]
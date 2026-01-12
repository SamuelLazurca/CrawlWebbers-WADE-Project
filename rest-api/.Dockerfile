# Folosim o imagine oficială de Python
FROM python:3.11-slim

# Setăm directorul de lucru
WORKDIR /code

# Copiem fișierul de dependențe
COPY ./requirements.txt /code/requirements.txt

# Instalăm dependențele
RUN pip install --no-cache-dir --upgrade -r /code/requirements.txt

# Copiem restul codului (folderul app)
COPY ./app /code/app

# Comanda de pornire (Cloud Run folosește variabila de mediu PORT)
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8080"]
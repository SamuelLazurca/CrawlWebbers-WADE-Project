FROM python:3.11-slim

WORKDIR /code

COPY ./requirements.txt /code/requirements.txt
RUN pip install --no-cache-dir --upgrade -r /code/requirements.txt

# Copiem tot conținutul din rest-api/ în /code/
COPY . /code/

# Acum main:app este direct în root, deci nu mai scriem app.main
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8080"]
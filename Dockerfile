FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

WORKDIR /app

COPY requirements.txt /app/
RUN pip install -r requirements.txt

COPY . /app/

# expose port 8000
EXPOSE 8000

# commande de lancement Django 
CMD ["gunicorn", "YummyBox_core.wsgi:application", "--bind", "0.0.0.0:8000"]


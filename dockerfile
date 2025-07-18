# Utilise une image officielle Python
FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV PIP_NO_TRUSTSTORE=1
ENV PIP_DISABLE_PIP_VERSION_CHECK=1

WORKDIR /App
COPY . .

RUN pip install --upgrade pip && pip install -r requirements.txt
RUN pip install -e .

RUN python App/manage.py collectstatic --noinput

# Exposer le port
EXPOSE 8000

CMD ["gunicorn", "App.wsgi:application", "--bind", "0.0.0.0:8000"]

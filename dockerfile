# Use official Python slim image
FROM python:3.12-slim

# 1) On se place à la racine du projet
WORKDIR /app

# 2) On copie tout
COPY . .

# 3) Variables d’environnement
ENV DJANGO_SETTINGS_MODULE=App.settings \
    PYTHONUNBUFFERED=1

# 4) Install des dépendances
RUN pip install --no-cache-dir --upgrade pip \
 && pip install --no-cache-dir -r requirements.txt \
 && pip install --no-cache-dir -e .

# 5) Collecte des statics
RUN python App/manage.py collectstatic --noinput

# 6) Expose le port
EXPOSE 8000

# 7) Lancement de Gunicorn en positionnant le cwd dans le dossier App
#    pour que wsgi.py soit trouvé directement
CMD ["python", "App/manage.py", "runserver", "0.0.0.0:8000"]

# Utilise une image officielle Python
FROM python:3.12-slim

# Définir le répertoire de travail
WORKDIR /app

# Copier le contenu du projet
COPY . .


# Installer les dépendances
RUN pip install --upgrade pip && \
pip install -r requirements.txt

RUN pip install -e .

# Exposer le port
EXPOSE 8000

# Commande de lancement du serveur Django
CMD ["python", "App/manage.py", "runserver", "0.0.0.0:8000"]

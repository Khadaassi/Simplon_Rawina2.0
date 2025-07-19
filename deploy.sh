#!/bin/bash

# Configuration
PROJECT_ID="rawina-466112"
REGION="europe-west1"
SERVICE_NAME="rawina"
IMAGE_NAME="gcr.io/$PROJECT_ID/$SERVICE_NAME"

# Étape 1 – Authentification et sélection du projet
gcloud config set project $PROJECT_ID

# Étape 2 – Build et push de l’image Docker vers Google Container Registry
gcloud builds submit --tag $IMAGE_NAME .

# Étape 3 – Déploiement sur Cloud Run avec injection de ton .env
gcloud run deploy $SERVICE_NAME \
  --image $IMAGE_NAME \
  --platform managed \
  --region $REGION \
  --allow-unauthenticated \
  --env-vars-file .env

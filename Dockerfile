# Utiliser une image Python officielle comme base
FROM python:3.9-slim

# Définir le répertoire de travail
WORKDIR /app

# Installer les dépendances système nécessaires pour tkinter
RUN apt-get update && apt-get install -y \
    python3-tk \
    && rm -rf /var/lib/apt/lists/*

# Copier les fichiers de dépendances
COPY requirements.txt .

# Installer les dépendances
RUN pip install --no-cache-dir -r requirements.txt

# Copier le reste des fichiers du projet
COPY . .

# Définir les variables d'environnement
ENV FLASK_APP=app.py
ENV FLASK_ENV=development
ENV FLASK_DEBUG=1
ENV PYTHONUNBUFFERED=1
ENV FLASK_RUN_HOST=0.0.0.0
ENV FLASK_RUN_PORT=5000

# Exposer le port sur lequel l'application Flask s'exécute
EXPOSE 5000

# Commande pour démarrer l'application
CMD ["python", "-u", "app.py"] 
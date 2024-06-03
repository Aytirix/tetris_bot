# Installation de Chromium et Chromedriver

Ce guide vous explique comment installer Chromium et Chromedriver dans le dossier `sgoinfre`.

## Étapes d'installation

1. Accédez au dossier `sgoinfre` :

   ```
   cd /home/$USER/sgoinfre
   ```

2. Téléchargez le binaire de Chromium et Chromedriver :

   ```
   wget https://storage.googleapis.com/chrome-for-testing-public/125.0.6422.141/linux64/chrome-linux64.zip
   wget https://storage.googleapis.com/chrome-for-testing-public/125.0.6422.141/linux64/chromedriver-linux64.zip
   ```

3. Extrayez les fichiers téléchargés :

   ```
   unzip chrome-linux64.zip
   unzip chromedriver-linux64.zip
   ```

## Configuration de l'environnement

1. Installez les dépendances nécessaires :

   ```
   pip3 install -r requirements.txt
   ```

2. Executez le programme :

   ```
   python3 main.py
   ```

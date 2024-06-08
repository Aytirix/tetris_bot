# Tetris Bot Documentation

## Fonctionnement de l'Algorithme du Bot Tetris

L'algorithme `algo_tetris` est conçu pour optimiser la stratégie de jeu dans Tetris. Il fonctionne selon les étapes suivantes :

### Évaluation des Actions
Pour chaque pièce actuelle, l'algorithme identifie toutes les actions valides (rotations et déplacements) et calcule leur valeur Q en simulant les résultats dans l'environnement Tetris.

### Sélection de l'Action
L'action qui maximise la valeur Q est choisie comme le meilleur mouvement. En cas d'égalité entre plusieurs actions, un choix aléatoire est effectué parmi les meilleures options.

### Validation et Optimisation
Chaque action est validée pour éviter les collisions et les placements hors limites, optimisant ainsi le placement des pièces pour améliorer le score et la gestion de l'espace.


## Configuration de l'environnement

1. Clonez le dépôt :

   ```
   git clone https://github.com/Aytirix/tetris_bot
   ```

2. Si possible, créez un environnement virtuel :

   ```
   python3 -m venv venv
   source venv/bin/activate
   ```

3. Installez les dépendances nécessaires :

   ```
   pip3 install -r requirements.txt
   ```

4. tester le bot en local :
   ```
   python3 main.py -l
   ```

5. Pour lancer le bot sur le jeu de saso :
   ```
   python3 main.py -s
   ```

## Configuration des Variables d'Environnement

Pour configurer le Tetris bot, définissez les variables nécessaires dans un fichier `.env` à la racine du projet. Les détails de chaque variable sont expliqués ci-dessous :

### Identification et Accès
- `USERNAME`: Nom d'utilisateur du bot pour la connexion aux services.
- `ROOM`: Nom de la salle ou du canal où le bot sera opérationnel.

### Paramètres du jeu Tetris
- `TETRIS_WIDTH`: Largeur du plateau de Tetris (nombre de colonnes, 10 par défaut).
- `TETRIS_HEIGHT`: Hauteur du plateau de Tetris (nombre de lignes, 20 par défaut).

### Scoring
- `MALUS_MOVE_ERROR`: Pénalité pour un mouvement invalide (-10000 par défaut).
- `BONUS_COMPLETE_LINE`: Bonus pour chaque ligne complétée (200 par défaut).
- `BONUS_FILLED_CELLS`: Bonus pour les cellules remplies, qui augmente avec la proximité de la base (0.3 par défaut).
- `MALUS_HOLE`: Pénalité pour chaque trou créé (60 par défaut).
- `MALUS_BUMPINESS`: Pénalité pour les différences de hauteur entre les colonnes (4 par défaut).
- `MALUS_HEIGHT_MAX`: Pénalité pour la hauteur maximale atteinte sur le plateau (3 par défaut).

### Configuration de l'exécution
- `LAST_MOVE`: Calculer les mouvements latéraux quand la pièce est en bas (False par défaut).
- `PRINT_MAP`: Contrôle l'affichage du plateau après chaque mouvement (True par défaut).
- `QQT_THREADS`: Nombre de parties simultanées traitées par le bot (1 par défaut).
- `QQT_EPISODES`: Nombre de parties jouées par chaque thread (1 par défaut).
- `INFINI_TRAINING`: Active l'entraînement continu sans fin spécifique (False par défaut).

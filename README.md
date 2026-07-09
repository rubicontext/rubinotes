# Rubinotes

Entraînement à la lecture de notes pour guitare (1ère position) + générateur de
progressions d'accords. PWA installable sur l'écran d'accueil mobile.

## Pages

- `/` — lecture de notes : une partition en clef de sol, on clique la position
  corde/case (0 à 3) sur le manche ; vert si juste, rouge sinon (avec la bonne
  position en surbrillance). Toggle pour afficher les notes naturelles sur le manche.
- `/accords` — générateur d'accords : tonalité + progression (I IV V…) avec
  libellés (pop, blues 12 mesures, cadence andalouse…), et table des accords
  diatoniques des 12 tonalités.

## Dev local

```bash
pip install -r requirements.txt
python manage.py runserver 0.0.0.0:8743 --noreload
```

Pas de base de données : l'app est entièrement sans état (logique en JS côté client).

## Déploiement

Même modèle que rubitrack sur lula (nginx + service uWSGI dédié + venv).
Point d'entrée WSGI : `rubinotes.wsgi:application`. Config env : cf. `.env.example`.
À faire : service `rubinotes-uwsgi`, vhost nginx, DNS. (Pas encore déployé.)

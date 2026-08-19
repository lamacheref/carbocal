# Changelog

Toutes les modifications notables de ce projet sont documentées ici.

Le format s'inspire de [Keep a Changelog](https://keepachangelog.com/fr/1.1.0/).
Le numéro de version suit le schéma `M.m.f` et le fichier `VERSION` fait foi.

## [Unreleased]

### Changé

- Réorientation du projet : le **convertisseur XLSX → ICS** devient la priorité (phase 1), l'automatisation se fera via **CalDAV** (phase 2), et l'**API SOAP** Carbonio est déconseillée (optionnel post-release).

## [Unreleased]

### Changé

- **Interface utilisateur** revue pour les utilisateurs finaux :
  - Vocabulaire : « Fichier Excel / Calc » (au lieu de XLSX), « fichier calendrier » (au lieu d'ICS), « Votre Email Carbonio » (au lieu de Compte CalDAV), mention CalDAV retirée de l'interface.
  - **Barre d'information fixe à droite** : formats pris en charge + téléchargement d'un **modèle vierge** (`/template`) avec les bonnes colonnes.
  - Fuseau horaire et serveur Carbonio **masqués par défaut** (bouton « Modifier »), valeurs par défaut `Europe/Paris` et `CARBOCAL_SERVER_URL`.
  - Boutons « Convertir en fichier calendrier » et « Importer dans Carbonio » **côte à côte**.
  - « Pause en seconde entre deux créations » : champ numérique à **spinner**, saisie manuelle bloquée, minimum **0.5**.
  - Page dimensionnée pour un écran desktop/laptop **sans barre de défilement verticale** (repli responsive sous 1000 px).
- Serveur Carbonio configurable via la variable d'environnement `CARBOCAL_SERVER_URL` (Docker `.env`).
- Au chargement des calendriers, le calendrier « Calendar » est affiché « Votre calendrier » (les autres libellés sont conservés).

### Ajouté

- **CI/CD Gitea Actions** (`.gitea/workflows/docker.yml`) : build + push de l'image `gitea.smiden.eu/flamachere/carbocal` sur push `main` et tags `v*` (secrets `CC_USER` / `CC_TOKEN` requis).
- **`docker-compose.prod.yml`** : déploiement en tirant l'image publiée (`docker compose -f docker-compose.prod.yml up -d`).

## [0.3.0] — 2026-08-19

### Ajouté

- **Import automatique CalDAV** (phase 2) : création directe des rendez-vous dans Carbonio avec envoi des invitations aux invités (`METHOD:REQUEST`).
- `converter/caldav_client.py` : connexion `<serveur>/dav/`, énumération des calendriers du compte, création d'événements.
- **CLI** : sous-commande `import` (`--server`, `--login`, `--password`, `--calendar`, `--delay`, `--dry-run`).
- **GUI web** : carte « Import direct dans Carbonio (CalDAV) » — serveur (défaut `https://mail.smiden.fr`), compte/mot de passe saisis à chaque import (jamais stockés), chargement de la liste des calendriers (défaut sélectionné : `Calendar`), pause configurable, rapport de création/erreurs.
- Endpoints web `POST /calendars` et `POST /import`.
- `METHOD` configurable dans le générateur ICS + VEVENT unitaire (`build_event_ics`).

### Vérifié

- Erreurs gérées proprement : URL invalide → 400, identifiants refusés par `https://mail.smiden.fr/dav/` → 502 « Unauthorized ».
- Non-régression `/convert` (200) et rendu du GUI (carte CalDAV présente).

### Changé

- Projet renommé **SendRendezvous → CarboCal** (titre, CLI, conteneurs Docker, domaine des UID, en-têtes web).

## [0.2.0] — 2026-08-19

### Ajouté

- Paquet `converter/` : parsing XLSX, détection des récurrences, génération ICS, CLI et GUI web.
- **CLI** : `python -m converter --input <xlsx> --output <ics> [--organizer <email>] [--tzid Europe/Paris]`.
- **GUI web** (FastAPI) : page d'upload XLSX → téléchargement du `.ics` (`python -m uvicorn converter.web:app`).
- Génération d'un **fichier `.ics` unique** importable dans Carbonio.
- Récurrences **RRULE** (`FREQ=WEEKLY;INTERVAL=n;BYDAY=…;UNTIL=…`) avec **RDATE/EXDATE** pour rester fidèle au fichier source (semaines sautées, décalages).
- Fuseau **Europe/Paris** avec bloc **VTIMEZONE**.
- Invités en **ATTENDEE**, organisateur paramétrable.
- **UID** stables et déterministes (réutilisables pour la phase 2 CalDAV).
- Événements « journée complète » (sans heures, ex. jours fériés).
- Rapport des lignes ignorées ou invalides sans bloquer la conversion.
- `requirements.txt`, `.gitignore`.
- **Docker** : `Dockerfile`, `docker-compose.yml`, `.dockerignore` (uvicorn non-root, healthcheck HTTP).

### Vérifié

- Conversion du fichier de référence (651 lignes → 26 séries récurrentes + 62 événements unitaires).
- Expansion des occurrences identique au fichier source (651 = 651).

## [0.1.0] — 2026-08-19

### Ajouté

- Initialisation du projet.
- Fichiers de référence : `TODO.md`, `ROADMAP.md`, `CHANGELOG.md`, `VERSION`, `README.md`.

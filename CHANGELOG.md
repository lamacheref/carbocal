# Changelog

Toutes les modifications notables de ce projet sont documentées ici.

Le format s'inspire de [Keep a Changelog](https://keepachangelog.com/fr/1.1.0/).
Le numéro de version suit le schéma `M.m.f` et le fichier `VERSION` fait foi.

## [Unreleased]

### Changé

- Réorientation du projet : le **convertisseur XLSX → ICS** devient la priorité (phase 1), l'automatisation se fera via **CalDAV** (phase 2), et l'**API SOAP** Carbonio est déconseillée (optionnel post-release).

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

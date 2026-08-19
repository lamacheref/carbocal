# CarboCal

Conversion et import massif de rendez-vous XLSX vers **Carbonio**.

> Version courante : `0.1.0` (voir `VERSION`).

## Objectif

Permettre à des utilisateurs finaux de convertir un fichier XLSX **normalisé** en rendez-vous importables dans Carbonio.

La stratégie a été réorientée :

- **Phase 1 (urgente) — Convertisseur XLSX → ICS** : génère **un unique fichier `.ics`** importable manuellement dans l'interface Calendrier de Carbonio. Événements **récurrents (RRULE + RDATE/EXDATE)**, fuseau **Europe/Paris** (VTIMEZONE), invités en **ATTENDEE**, organisateur = compte qui importe. Livré sous forme **CLI + petit GUI web**.
- **Phase 2 — Ajout automatique via CalDAV** : création des rendez-vous directement dans Carbonio. **CalDAV est validé par notre provider** et est la voie privilégiée.
- **Optionnel — API SOAP Carbonio** : déconseillé par le provider, à n'envisager qu'en post-release.

## Décisions d'architecture

| Sujet | Décision |
|---|---|
| Livrable prioritaire | Convertisseur XLSX → `.ics` unique |
| Récurrences | RRULE (`FREQ=WEEKLY;INTERVAL=n`) + RDATE/EXDATE pour fidélité au source |
| Fuseau horaire | `Europe/Paris` avec bloc VTIMEZONE |
| Invités | `ATTENDEE` ; organisateur = compte importateur (saisi dans l'outil) |
| Interface phase 1 | CLI + petit GUI web (FastAPI) |
| Automatisation phase 2 | Client **CalDAV** |
| API SOAP | Non recommandé, éventuellement post-release |

## Références

- `PROJET.md` : cahier des charges et architecture détaillée (historique).
- `ref/20260813_Calendrier_Consolide_Carbonio_FINAL_Marie.xlsx` : fichier source de définition des rendez-vous (feuille `Import_Carbonio`, colonnes `Sujet | Date | Heure début | Heure fin | Lieu | Invités`).

## Contenu du dépôt

| Fichier / dossier | Rôle |
|---|---|
| `PROJET.md` | Spécifications et architecture |
| `TODO.md` | Tâches en cours et à venir |
| `ROADMAP.md` | Jalons et plan d'exécution |
| `CHANGELOG.md` | Historique des versions |
| `VERSION` | Version courante (`M.m.f`) |
| `ref/` | Fichiers de référence (XLSX, etc.) |
| `converter/` | Code du convertisseur (parsing, récurrence, ICS, CLI, web) |
| `requirements.txt` | Dépendances Python |
| `Dockerfile`, `docker-compose.yml` | Déploiement conteneur |
| `.venv/` | Environnement virtuel (non versionné) |

## Utilisation (v0.3.0)

### En local

```bash
.venv/bin/pip install -r requirements.txt   # 1re fois
.venv/bin/uvicorn converter.web:app          # GUI : http://127.0.0.1:8000

# CLI : conversion XLSX -> .ics
.venv/bin/python -m converter --input ref/xxx.xlsx --output calendrier.ics --organizer prenom.nom@domaine.fr

# CLI : import direct dans Carbonio (CalDAV) avec invitations
.venv/bin/python -m converter import --input ref/xxx.xlsx \
  --server https://mail.smiden.fr --login prenom.nom@domaine.fr --calendar Calendar
```

### Avec Docker

#### Développement (build local)

```bash
docker compose up -d --build        # http://<serveur>:8123
```

#### Production (image construite par Gitea Actions)

```bash
docker compose -f docker-compose.prod.yml up -d
```

Le serveur Carbonio est défini par la variable `CARBOCAL_SERVER_URL` (défaut `https://mail.smiden.fr`), masquée dans l'interface (champ « à faire apparaître »).

## CI/CD (Gitea Actions)

Le workflow `.gitea/workflows/docker.yml` construit l'image sur chaque push sur `main` (et les tags `v*`) et la publie sur le registre Gitea : `gitea.smiden.eu/flamachere/carbocal` (tags `latest`, `vX.Y.Z`, `sha-…`).

**Prérequis** : créer deux secrets dans *Réglages du dépôt → Actions* :
- `CC_USER` : utilisateur du registre (ex. nom de compte Gitea ou compte dédié) ;
- `CC_TOKEN` : Personal Access Token Gitea avec la permission **`write:package`** (et `read:repository`).

Vérifier le build dans *Actions* ; une fois l'image publiée :

```bash
docker compose -f docker-compose.prod.yml up -d
```

## État d'avancement

Le **Jalon 1 — Convertisseur XLSX → ICS** est implémenté (v0.2.0), le **Jalon 2 — Import CalDAV** (v0.3.0) aussi. Reste la **recette** : import du `.ics` dans Carbonio et un premier import CalDAV réel avec un compte valide. L'option API SOAP reste non retenue. Voir `ROADMAP.md`.

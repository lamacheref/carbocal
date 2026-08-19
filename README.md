# SendRendezvous

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
| `.venv/` | Environnement virtuel (non versionné) |

## État d'avancement

Le projet est à l'étape d'**initialisation** (objectif 1 terminé). Le **Jalon 1 — Convertisseur XLSX → ICS** est le prochain objectif. Voir `ROADMAP.md` pour les détails.

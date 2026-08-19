# SendRendezvous

Import massif de rendez-vous XLSX vers **Carbonio** par lots, via une petite application web interne.

> Version courante : `0.1.0` (voir `VERSION`).

## Objectif

Permettre à des utilisateurs finaux de :
1. charger un fichier XLSX **normalisé** ;
2. valider son contenu ;
3. le convertir en rendez-vous Carbonio ;
4. créer les rendez-vous par **lots** pour limiter l'impact sur la plateforme distante.

Deux modes sont prévus :
- **Mode API SOAP** (recommandé) : création directe dans Carbonio via `CreateAppointment`, avec invitations, journal d'erreurs et découpe par lots.
- **Mode export ICS** (secours) : génération de fichiers `.ics` pour import manuel.

## Références

- `PROJET.md` : cahier des charges et architecture détaillée.
- `ref/20260813_Calendrier_Consolide_Carbonio_FINAL_Marie.xlsx` : fichier source de définition des rendez-vous (feuille `Import_Carbonio`).

## Contenu du dépôt

| Fichier | Rôle |
|---|---|
| `PROJET.md` | Spécifications et architecture |
| `TODO.md` | Tâches en cours et à venir |
| `ROADMAP.md` | Jalons et plan d'exécution |
| `CHANGELOG.md` | Historique des versions |
| `VERSION` | Version courante (`M.m.f`) |
| `ref/` | Fichiers de référence (XLSX, etc.) |

## État d'avancement

Le projet est à l'étape d'**initialisation** (objectif 1). Voir `ROADMAP.md` pour les prochains jalons.

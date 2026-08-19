# ROADMAP

Plan d'exécution du projet **Import massif de rendez-vous XLSX vers Carbonio**.

Référence détaillée : `PROJET.md`. Version actuelle : `VERSION`.

## Vision

Convertir un XLSX **normalisé** en rendez-vous importables dans Carbonio, puis automatiser leur création.

- **Phase 1 (urgente)** : un unique fichier `.ics` importable manuellement dans Carbonio (RRULE + RDATE/EXDATE, VTIMEZONE Europe/Paris, ATTENDEE).
- **Phase 2** : création automatique via **CalDAV** (validé par le provider).
- **Optionnel** : API SOAP Carbonio, déconseillée, uniquement post-release.

## Jalons

### Jalon 0 — Initialisation du projet
- Statut : ✅ terminé
- Livrables : `TODO.md`, `ROADMAP.md`, `CHANGELOG.md`, `VERSION`, `README.md`.

### Jalon 1 — Convertisseur XLSX → ICS (urgent)
- Statut : 🔄 en cours
- Objectif : produire un `.ics` unique, fidèle au fichier source, importable manuellement dans l'interface Calendrier de Carbonio.
- Livrables : parsing XLSX, détection des récurrences (RRULE + RDATE/EXDATE), VTIMEZONE `Europe/Paris`, `ATTENDEE`/organisateur, **CLI** + **GUI web FastAPI**, validation du `.ics`.
- Critère de sortie : conversion du fichier de référence et import validé dans Carbonio.

### Jalon 2 — Ajout automatique via CalDAV (phase 2)
- Statut : ⬜ à venir
- Objectif : créer les rendez-vous directement dans Carbonio via CalDAV.
- Livrables : client CalDAV, mapping récurrence/invités, mode import automatique (lots, journal).
- Prérequis : accès CalDAV fourni par le provider (validé).

### Jalon 3 — API SOAP Carbonio (optionnel, post-release)
- Statut : ⬜ non retenu pour l'instant
- Objectif : `CreateAppointment` si le provider autorise l'API SOAP.
- Note : voie déconseillée par le provider ; à réévaluer après la release.

### Jalon 4 — Recette
- Statut : ⬜ à venir
- Objectif : valider les scénarios nominaux et en erreur.
- Livrable : PV de recette.

## Règles de versioning

- Schéma `M.m.f` : `M` = majeur, `m` = mineur, `f` = correctif.
- Fichier de référence : `VERSION`.
- Chaque livraison mise à jour dans `CHANGELOG.md`.

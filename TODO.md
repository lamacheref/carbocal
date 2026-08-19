# TODO

Suivi des tâches du projet **Import massif de rendez-vous XLSX vers Carbonio**.

> Version en cours : voir `VERSION`. Plan d'ensemble : voir `ROADMAP.md`.

## Initialisation (objectif 1)

- [x] Fichiers de base du projet : `TODO.md`, `ROADMAP.md`, `CHANGELOG.md`, `VERSION`, `README.md`.

## Jalon 1 — Convertisseur XLSX → ICS (urgent)

### Parsing du XLSX (`ref/20260813_Calendrier_Consolide_Carbonio_FINAL_Marie.xlsx`, feuille `Import_Carbonio`)

- [ ] Lire les colonnes `Sujet | Date | Heure début | Heure fin | Lieu | Invités`.
- [ ] Normaliser les dates (mix `datetime` et chaînes `DD/MM/YYYY` et `DD/MM/YYYY – Mercredi`).
- [ ] Normaliser les heures (mix `time` et chaînes `HH:MM`).
- [ ] Découper `Invités` sur `;` et ignorer les valeurs vides.
- [ ] Rapporter les lignes invalides (date/heure absente ou illisible, fin ≤ début) sans bloquer la conversion.

### Récurrence

- [ ] Grouper les lignes en séries (sujet + horaires + lieu + invités identiques).
- [ ] Détecter la cadence hebdomadaire (`FREQ=WEEKLY;INTERVAL=1`) ou bimensuelle (`INTERVAL=2`) + jour (`BYDAY`).
- [ ] Gérer les semaines manquantes et irrégularités : **RDATE** pour les dates hors cadence, **EXDATE** pour les dates générées absentes du source.
- [ ] Séries ponctuelles et irrégulières → événements unitaires (sans RRULE).

### Génération ICS

- [ ] Un unique fichier `.ics` complet.
- [ ] Fuseau `Europe/Paris` avec bloc `VTIMEZONE`.
- [ ] `ATTENDEE` par invité, organisateur = compte importateur (paramétré).
- [ ] `UID` stables et déterministes (réutilisables en phase 2 CalDAV).
- [ ] Validation du `.ics` produit (parsing icalendar + relecture).

### Interfaces

- [ ] **CLI** : `--input` XLSX, `--output` `.ics`, `--organizer` email, options de format.
- [ ] **GUI web** (FastAPI) : upload XLSX, saisie de l'organisateur, téléchargement du `.ics`.

### Recette

- [ ] Convertir le fichier de référence (651 lignes, 31 séries).
- [ ] Vérifier le résultat dans l'interface Calendrier de Carbonio (import manuel).
- [ ] Contrôler séries hebdomadaires, bimensuelles, ponctuelles, invités multiples, semaines sautées.

## Jalon 2 — Ajout automatique via CalDAV (phase 2)

- [ ] Choisir la librairie CalDAV (ex. `caldav`) et confirmer l'accès (URL, compte).
- [ ] Établir la connexion et tester la création d'un rendez-vous simple.
- [ ] Adapter la récurrence (RRULE) et les `ATTENDEE` à l'API CalDAV.
- [ ] Ajouter le mode « import automatique » (éventuellement par lots + journal d'erreurs).

## Optionnel — API SOAP Carbonio (post-release, déconseillé)

- [ ] À n'envisager que si le provider l'autorise ; prévoir `AuthRequest` / `CreateAppointment`.

## Recette globale

- [ ] Test avec 3 rendez-vous.
- [ ] Test avec 25 rendez-vous.
- [ ] Test avec invités multiples.
- [ ] Test avec erreurs de date, d'email et doublons (`uid`).
- [ ] Test sur une instance Carbonio de préproduction si possible.

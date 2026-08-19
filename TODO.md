# TODO

Suivi des tâches du projet **Import massif de rendez-vous XLSX vers Carbonio**.

> Version en cours : voir `VERSION`. Plan d'ensemble : voir `ROADMAP.md`.

## Initialisation (objectif 1)

- [x] Fichiers de base du projet : `TODO.md`, `ROADMAP.md`, `CHANGELOG.md`, `VERSION`, `README.md`.

## Jalon 1 — Convertisseur XLSX → ICS (urgent)

### Parsing du XLSX (`ref/20260813_Calendrier_Consolide_Carbonio_FINAL_Marie.xlsx`, feuille `Import_Carbonio`)

- [x] Lire les colonnes `Sujet | Date | Heure début | Heure fin | Lieu | Invités`.
- [x] Normaliser les dates (mix `datetime` et chaînes `DD/MM/YYYY` et `DD/MM/YYYY – Mercredi`).
- [x] Normaliser les heures (mix `time` et chaînes `HH:MM`).
- [x] Découper `Invités` sur `;` et ignorer les valeurs vides.
- [x] Événements « journée complète » (sans heures) et rapport des lignes invalides.

### Récurrence

- [x] Grouper les lignes en séries (sujet + horaires + lieu + invités identiques).
- [x] Détecter la cadence hebdomadaire (`FREQ=WEEKLY;INTERVAL=1`) ou bimensuelle (`INTERVAL=2`) + jour (`BYDAY`).
- [x] Gérer les semaines manquantes et irrégularités : **RDATE** pour les dates hors cadence, **EXDATE** pour les dates générées absentes du source.
- [x] Séries ponctuelles et irrégulières → événements unitaires (sans RRULE).

### Génération ICS

- [x] Un unique fichier `.ics` complet.
- [x] Fuseau `Europe/Paris` avec bloc `VTIMEZONE`.
- [x] `ATTENDEE` par invité, organisateur = compte importateur (paramétré).
- [x] `UID` stables et déterministes (réutilisables en phase 2 CalDAV).
- [x] Validation du `.ics` produit (expansion 651 occurrences = 651 lignes source).

### Interfaces

- [x] **CLI** : `--input` XLSX, `--output` `.ics`, `--organizer` email, `--tzid`.
- [x] **GUI web** (FastAPI) : upload XLSX, saisie de l'organisateur, téléchargement du `.ics`.
- [x] **Docker** : `Dockerfile` + `docker-compose.yml` (build et conversion testés dans un conteneur).

### Recette

- [ ] Convertir le fichier de référence (651 lignes, 31 séries) — fait côté code, reste à valider dans Carbonio.
- [ ] Vérifier le résultat dans l'interface Calendrier de Carbonio (import manuel).
- [ ] Contrôler séries hebdomadaires, bimensuelles, ponctuelles, invités multiples, semaines sautées, journées complètes.

## Jalon 2 — Ajout automatique via CalDAV (phase 2)

- [x] Choisir la librairie CalDAV (`caldav` 3.2.1) et le schéma d'accès `<serveur>/dav/`.
- [x] Établir la connexion et l'énumération des calendriers du compte (`/calendars`).
- [x] Création d'un rendez-vous avec invitations (`METHOD:REQUEST`) et récurrence RRULE préservée.
- [x] GUI : carte « Import direct dans Carbonio » (serveur, compte, mot de passe non stocké, sélection du calendrier, pause, rapport).
- [x] CLI : sous-commande `import` (avec `--dry-run`).
- [ ] **Recette** : import réel sur le serveur avec un compte valide, vérifier la création et la réception des invitations (MOOC).

## Optionnel — API SOAP Carbonio (post-release, déconseillé)

- [ ] À n'envisager que si le provider l'autorise ; prévoir `AuthRequest` / `CreateAppointment`.

## Recette globale

- [ ] Test avec 3 rendez-vous.
- [ ] Test avec 25 rendez-vous.
- [ ] Test avec invités multiples.
- [ ] Test avec erreurs de date, d'email et doublons (`uid`).
- [ ] Test sur une instance Carbonio de préproduction si possible.

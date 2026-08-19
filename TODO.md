# TODO

Suivi des tâches du projet **Import massif de rendez-vous XLSX vers Carbonio**.

> Version en cours : voir `VERSION`.

## Initialisation (objectif 1)

- [x] Fichiers de base du projet : `TODO.md`, `ROADMAP.md`, `CHANGELOG.md`, `VERSION`, `README.md`.

## Étape 1 — Vérification de Carbonio

- [ ] Tester `POST https://mail.domaine/service/soap`.
- [ ] Valider `AuthRequest` avec un compte réel et récupérer un `authToken`.
- [ ] Réaliser un test unitaire `CreateAppointment` avec un rendez-vous simple.
- [ ] Documenter le résultat (mode SOAP opérationnel ou non).

## Étape 2 — Définition du modèle XLSX

- [ ] Confronter le format réel de `ref/20260813_Calendrier_Consolide_Carbonio_FINAL_Marie.xlsx` (feuille `Import_Carbonio` : `Sujet`, `Date`, `Heure début`, `Heure fin`, `Lieu`, `Invités`) au format normalisé de `PROJET.md` (`uid`, `subject`, `start`, `end`, `timezone`, `location`, `description`, `organizer_email`, `attendees`, `label`, `send_invite`).
- [ ] Définir le mapping entre colonnes du fichier réel et structure interne.
- [ ] Fournir un fichier modèle vierge.
- [ ] Définir les règles de validation : dates (`DD/MM/YYYY` + `HH:MM`), emails, timezone (`Europe/Paris`), valeurs booléennes.

## Étape 3 — Prototype CLI

- [ ] Lire le XLSX (`openpyxl`).
- [ ] Contrôler les lignes et générer un rapport d'erreurs.
- [ ] Créer un rendez-vous de test dans Carbonio.
- [ ] Ajouter le traitement par lots.

## Étape 4 — Prototype GUI minimal

- [ ] Page web unique : upload XLSX, prévisualisation, champs Carbonio.
- [ ] Boutons `Valider`, `Simulation`, `Importer`.
- [ ] Barre de progression et journal lisible.

## Étape 5 — Industrialisation

- [ ] Reprise après échec.
- [ ] Export du rapport (CSV / JSON).
- [ ] Génération ICS de secours.
- [ ] Verrou d'exécution anti-imports concurrents.

## Étape 6 — Recette

- [ ] Test avec 3 rendez-vous.
- [ ] Test avec 25 rendez-vous.
- [ ] Test avec invités multiples.
- [ ] Test avec erreurs de date, d'email et doublons (`uid`).
- [ ] Test sur une instance Carbonio de préproduction si possible.

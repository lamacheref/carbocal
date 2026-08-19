# ROADMAP

Plan d'exécution du projet **Import massif de rendez-vous XLSX vers Carbonio**.

Référence détaillée : `PROJET.md`. Version actuelle : `VERSION`.

## Vision

Petite application web interne : charger un XLSX normalisé → valider → convertir en rendez-vous Carbonio → créer par lots via API SOAP (mode principal) ou générer des `.ics` (mode secours).

## Jalons

### Jalon 0 — Initialisation du projet
- Statut : ✅ terminé
- Livrables : `TODO.md`, `ROADMAP.md`, `CHANGELOG.md`, `VERSION`, `README.md`.

### Jalon 1 — Vérification de Carbonio (Étape 1)
- Statut : ⬜ à venir
- Objectif : prouver que `AuthRequest` et `CreateAppointment` fonctionnent sur l'instance cible.
- Livrable : note de validation + petit script de test.

### Jalon 2 — Modèle XLSX (Étape 2)
- Statut : ⬜ à venir
- Objectif : fixer le mapping entre le fichier de référence (`ref/20260813_Calendrier_Consolide_Carbonio_FINAL_Marie.xlsx`, feuille `Import_Carbonio`) et le format normalisé.
- Livrables : modèle vierge, règles de validation.

### Jalon 3 — Prototype CLI (Étape 3)
- Statut : ⬜ à venir
- Objectif : lire, valider, créer et batcher depuis la ligne de commande.
- Livrable : moteur d'import testable.

### Jalon 4 — Prototype GUI (Étape 4)
- Statut : ⬜ à venir
- Objectif : interface web minimale (upload, prévisualisation, simulation, import).
- Livrable : application FastAPI + HTML simple.

### Jalon 5 — Industrialisation (Étape 5)
- Statut : ⬜ à venir
- Objectif : reprise, rapports exportables, mode ICS de secours, verrou d'exécution.
- Livrable : application robuste prête pour la recette.

### Jalon 6 — Recette (Étape 6)
- Statut : ⬜ à venir
- Objectif : valider les scénarios nominaux et en erreur sur préproduction.
- Livrable : PV de recette.

## Règles de versioning

- Schéma `M.m.f` : `M` = majeur, `m` = mineur, `f` = correctif.
- Fichier de référence : `VERSION`.
- Chaque livraison mise à jour dans `CHANGELOG.md`.

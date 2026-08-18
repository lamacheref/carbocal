# Projet d'import massif de rendez-vous XLSX vers Carbonio

Les fichiers de références pour le développement se trouvent dans le dossier ref/

## Objectif

Créer une petite interface graphique, simple pour des utilisateurs finaux, permettant de charger un fichier XLSX **normalisé**, de le valider, de le convertir en rendez-vous Carbonio, puis de pousser les créations par **lots** afin de limiter l'impact sur la plateforme distante. Carbonio permet l'import de calendriers au format `.ics`, et expose aussi une API SOAP permettant de créer des rendez-vous avec participants et invitations.[cite:50][cite:21][cite:53]

## Contexte technique

Carbonio accepte l'import manuel de fichiers `.ics` depuis l'interface calendrier.[cite:50] Carbonio expose également une authentification SOAP sur `/service/soap`, avec récupération d'un `authToken` à réutiliser dans les requêtes suivantes.[cite:37][cite:38] La commande `CreateAppointment` permet de créer un rendez-vous et d'envoyer éventuellement des invitations à d'autres participants.[cite:21][cite:53]

## Décision d'architecture

La solution la plus efficace pour un usage utilisateur est une **petite application web interne** avec interface très simple.

Elle doit proposer deux modes :

- **Mode API SOAP** : création directe dans Carbonio avec invitations, suivi d'état, journal d'erreurs et découpe par lots ; c'est le mode principal recommandé.[cite:21][cite:37]
- **Mode export ICS** : génération d'un fichier `.ics` unique ou de plusieurs `.ics` par lot, pour import manuel si l'API n'est pas disponible ou si l'on veut un plan B.[cite:50][cite:54]

## Périmètre fonctionnel

L'interface doit rester minimale :

- Sélection d'un fichier XLSX.
- Vérification du format attendu.
- Prévisualisation des lignes valides et invalides.
- Paramétrage du lot : taille, pause entre lots, mode simulation, mode API ou ICS.
- Saisie des paramètres Carbonio : URL, compte, mot de passe ou jeton.
- Lancement de l'import.
- Affichage de la progression.
- Export d'un journal CSV ou JSON des succès et des erreurs.

## Format XLSX normalisé recommandé

Chaque ligne représente un rendez-vous.

| Colonne | Obligatoire | Description |
|---|---|---|
| `uid` | Oui | Identifiant unique stable de l'événement. |
| `subject` | Oui | Titre du rendez-vous. |
| `start` | Oui | Date/heure de début en ISO 8601 ou format homogène. |
| `end` | Oui | Date/heure de fin. |
| `timezone` | Oui | Fuseau horaire, par exemple `Europe/Paris`. |
| `location` | Non | Lieu du rendez-vous. |
| `description` | Non | Notes ou contenu du rendez-vous. |
| `organizer_email` | Oui | Adresse organisatrice utilisée dans Carbonio. |
| `attendees` | Non | Liste d'adresses séparées par `;`. |
| `label` | Non | Catégorie métier ou tag fonctionnel. |
| `send_invite` | Non | Booléen indiquant si une invitation doit être envoyée. |

## Architecture applicative recommandée

### Interface

Une page web unique suffit :

- formulaire de dépôt XLSX ;
- bloc de configuration Carbonio ;
- bloc de validation ;
- bloc de lancement ;
- tableau de progression ;
- zone de logs.

### Backend

Un petit backend Python est le plus rationnel pour ce besoin :

- `FastAPI` ou `Flask` pour exposer l'interface et les endpoints ;
- `openpyxl` ou `pandas` pour lire le XLSX ;
- `icalendar` si mode ICS ;
- `httpx` ou `requests` pour parler à l'API SOAP Carbonio ;
- file d'exécution simple en mémoire, sans dépendance lourde.

### Modules internes

- `xlsx_parser` : lecture du fichier.
- `validator` : validation métier et technique.
- `transformer` : mapping ligne XLSX vers structure rendez-vous.
- `carbonio_client` : auth SOAP, création d'appointments, contrôle des réponses.
- `ics_builder` : génération de fichiers `.ics`.
- `batch_runner` : découpe, temporisation, reprise sur erreur.
- `reporter` : journaux et exports.

## Pourquoi privilégier l'API SOAP

L'API SOAP Carbonio permet l'authentification par `AuthRequest` puis l'envoi de requêtes authentifiées grâce au `authToken`.[cite:37][cite:38] La commande `CreateAppointment` est explicitement prévue pour créer un rendez-vous, avec composant d'invitation et participants.[cite:21][cite:53] Ce mode est donc mieux adapté que l'import ICS lorsqu'il faut gérer des invitations, des erreurs unitaires et des traitements pilotés par lots.[cite:21][cite:50]

## Stratégie de découpe par lots

Le découpage par lots doit être natif dans l'application.

Paramètres recommandés :

- taille de lot par défaut : **25 rendez-vous** ;
- pause entre lots : **3 à 10 secondes** ;
- journalisation après chaque lot ;
- possibilité de reprise au lot suivant en cas d'échec partiel ;
- mode simulation avant exécution réelle.

Exemple de flux :

1. Chargement du XLSX.
2. Validation de toutes les lignes.
3. Constitution d'une file de travaux.
4. Découpage en lots de 25.
5. Authentification Carbonio.
6. Envoi séquentiel des rendez-vous du lot.
7. Pause contrôlée.
8. Passage au lot suivant.
9. Génération du rapport final.

## Règles de sécurité et robustesse

- Ne jamais stocker le mot de passe en clair dans le navigateur.
- Préférer un jeton ou une session backend courte si possible.
- Masquer les secrets dans les logs.
- Limiter la concurrence : **un seul import à la fois** au départ.
- Ajouter un mode **dry-run** qui ne fait que valider et simuler.
- Détecter les doublons par `uid` avant création.
- Prévoir un timeout et une politique de retry limitée.

## Étapes de réalisation

### Étape 1 — Vérification de Carbonio

- Tester `POST https://mail.domaine/service/soap`.
- Valider `AuthRequest` avec un compte réel.
- Vérifier la récupération d'un `authToken`.[cite:37][cite:38]
- Réaliser un test unitaire `CreateAppointment` avec un rendez-vous simple.[cite:21]

### Étape 2 — Définition du modèle XLSX

- Fixer les colonnes exactes.
- Fournir un fichier modèle vierge.
- Définir les règles de validation : dates, emails, timezone, valeurs booléennes.

### Étape 3 — Prototype CLI

- Lire le XLSX.
- Contrôler les lignes.
- Générer un rapport d'erreurs.
- Créer un rendez-vous de test dans Carbonio.
- Ajouter le traitement par lots.

### Étape 4 — Prototype GUI minimal

- Créer une page simple avec upload.
- Ajouter la prévisualisation des données.
- Ajouter les champs Carbonio.
- Ajouter les boutons `Valider`, `Simulation`, `Importer`.
- Ajouter une barre de progression et un journal lisible.

### Étape 5 — Industrialisation

- Ajouter reprise après échec.
- Ajouter export du rapport.
- Ajouter génération ICS de secours.[cite:50][cite:54]
- Ajouter verrou d'exécution pour éviter les imports concurrents.

### Étape 6 — Recette

- Tester avec 3 rendez-vous.
- Tester avec 25 rendez-vous.
- Tester avec des invités multiples.[cite:21][cite:52]
- Tester avec erreurs de date, d'email et de doublons.
- Tester sur une instance Carbonio de préproduction si possible.

## Interface utilisateur proposée

L'interface doit être très simple :

1. **Choisir le fichier XLSX**.
2. **Vérifier** : nombre de lignes, erreurs, avertissements.
3. **Configurer l'import** : taille des lots, pause, mode API/ICS.
4. **Saisir l'accès Carbonio**.
5. **Lancer une simulation**.
6. **Lancer l'import réel**.
7. **Télécharger le rapport**.

## Livrables conseillés

- application web interne ;
- modèle XLSX ;
- documentation d'exploitation ;
- journal CSV ou JSON des imports ;
- mode export ICS de secours.[cite:50]

## Choix techniques recommandés

| Élément | Recommandation |
|---|---|
| Langage | Python |
| Interface | FastAPI + HTML simple + JS léger |
| Lecture XLSX | `openpyxl` |
| Appels HTTP | `httpx` |
| ICS | `icalendar` |
| Logs | JSON + CSV exportable |
| Exécution | séquentielle par lots |
| Déploiement | conteneur Docker léger |

## Ordre de travail conseillé

- Valider Carbonio SOAP.
- Produire le modèle XLSX.
- Développer le moteur d'import en CLI.
- Ajouter le batching et le dry-run.
- Construire l'interface graphique.
- Ajouter le mode ICS de secours.
- Documenter et tester.

## Point d'attention final

L'import ICS est simple et supporté côté utilisateur, mais il est mieux adapté à un import de calendrier qu'à un vrai traitement transactionnel avec invitations, contrôle fin des erreurs et reprise.[cite:50][cite:54] Pour une interface destinée à des utilisateurs finaux avec import massif et limitation d'impact sur la plateforme distante, le meilleur compromis est donc : **GUI simple + backend Python + API SOAP Carbonio + batching contrôlé + export ICS en secours**.[cite:21][cite:37][cite:53]

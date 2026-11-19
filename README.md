# Gestion d'un centre de formation

**Devoir 03 – Mini-projets de programmation en Python – Sujet 4**

## Participants

- Ruud Jean Gilles
- Ruth-Zaëlle Louis

## Description

Application de gestion en console pour un centre de formation : étudiants,
formateurs, cours, inscriptions, évaluations et résultats. Elle est écrite en
Python (bibliothèque standard uniquement, aucune installation de paquet) avec
de la programmation orientée objet : encapsulation, héritage
(`Personne` → `Etudiant` et `Formateur`) et redéfinition de méthodes.

## Fonctionnalités principales

- Gestion des étudiants et des formateurs (ajout, liste triée, recherche).
- Création de cours avec un formateur, une capacité et des créneaux hebdomadaires.
- Inscriptions, désinscriptions et **listes d'attente**.
- Évaluations avec **coefficients** et calcul des moyennes pondérées.
- Résultats individuels, taux de réussite, taux de remplissage des cours,
  classement des étudiants.
- **Historique** de toutes les opérations importantes.
- **Sauvegarde automatique en JSON** après chaque modification.

## Règles de gestion

- La capacité d'un cours est toujours supérieure à 0 ; on ne peut pas dépasser
  le nombre de places.
- Un étudiant ne peut pas être inscrit à deux cours dont les créneaux se
  chevauchent. Un formateur ne peut pas animer deux cours qui se chevauchent.
  Un créneau qui commence quand un autre se termine n'est pas un conflit.
- Si un cours est plein, l'étudiant est placé en liste d'attente. Quand une
  place se libère, elle est attribuée au **premier candidat admissible** (sans
  conflit d'horaire) ; les candidats non admissibles gardent leur rang.
- Une note est comprise entre 0 et 100 et ne peut être donnée qu'à un étudiant
  inscrit au cours. Une désinscription supprime aussi ses notes du cours.
- **Notes manquantes** : elles sont ignorées dans la moyenne (leur coefficient
  aussi). Sans aucune note, la moyenne est « N/A ».
- Un cours est réussi à partir d'une moyenne de 60/100. Le taux de réussite
  est calculé parmi les étudiants qui ont au moins une note.
- Une opération refusée ne modifie jamais les données : toutes les
  vérifications sont faites avant toute modification.

## Structure du dépôt

| Fichier | Rôle |
|---|---|
| `main.py` | Menu interactif, saisies contrôlées, affichage |
| `centre.py` | Classe `Centre` : règles de gestion, indicateurs, conversion JSON |
| `personne.py` | Classes `Personne`, `Etudiant`, `Formateur` |
| `cours.py` | Classe `Cours` et détection des conflits de créneaux |
| `evaluation.py` | Classe `Evaluation` (coefficient et notes) |
| `stockage.py` | Chargement et sauvegarde JSON |
| `donnees_demo.json` | Données de démonstration |
| `rapport.pdf` | Document de présentation (2 à 3 pages) |

## Lancer l'application

Prérequis : Python 3.8 ou plus récent.

```bash
python main.py donnees_demo.json
```

Pour démarrer avec des données vides, lancer simplement :

```bash
python main.py
```

Le fichier `donnees_centre.json` est alors créé automatiquement à la première
sauvegarde. Le fichier indiqué en argument est modifié au fil des opérations :
pour rejouer la démonstration depuis zéro, repartir d'une copie de
`donnees_demo.json`.

Si le fichier JSON existe mais est invalide, le programme affiche l'erreur et
s'arrête sans écraser le fichier.

## Tester les modules

Chaque module contient un petit scénario de test lancé directement :

```bash
python personne.py
python cours.py
python centre.py
python stockage.py
```

## Exemple d'utilisation

1. Lancer `python main.py donnees_demo.json`.
2. Menu **Inscriptions** → **Inscrire** l'étudiant 1 au cours 2 : refusé, car
   il y a un conflit d'horaire avec le cours Python.
3. Menu **Inscriptions** → **Désinscrire** l'étudiant 1 du cours 1 (plein) :
   la place est donnée au premier étudiant admissible de la liste d'attente.
4. Quitter puis relancer : les inscriptions et l'historique sont conservés.

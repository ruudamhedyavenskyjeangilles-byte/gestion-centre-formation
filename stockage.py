import json
import os

from centre import Centre

NOM_FICHIER = "donnees_centre.json"


class FichierInvalideError(Exception):
    """Le fichier de sauvegarde existe mais n'est pas utilisable."""


def charger(chemin=NOM_FICHIER):
    """Retourne un Centre.
    - fichier absent (premier lancement) : Centre vide ;
    - fichier invalide : lève FichierInvalideError, sans modifier le fichier."""
    if not os.path.exists(chemin):
        return Centre()

    try:
        with open(chemin, "r", encoding="utf-8") as fichier:
            data = json.load(fichier)
        return Centre.depuis_dict(data)
    except KeyError as erreur:
        raise FichierInvalideError(
            f"Le fichier {chemin} est invalide : champ manquant {erreur}.") from erreur
    except (ValueError, TypeError, AttributeError) as erreur:
        # json.JSONDecodeError est une sous-classe de ValueError
        raise FichierInvalideError(
            f"Le fichier {chemin} est invalide : {erreur}") from erreur
    except OSError as erreur:
        raise FichierInvalideError(
            f"Le fichier {chemin} est illisible : {erreur}") from erreur


def sauvegarder(centre, chemin=NOM_FICHIER):
    """Écrit d'abord dans un fichier temporaire puis le renomme : si le
    programme s'arrête en pleine écriture, l'ancien fichier reste intact."""
    temporaire = chemin + ".tmp"
    with open(temporaire, "w", encoding="utf-8") as fichier:
        json.dump(centre.to_dict(), fichier, ensure_ascii=False, indent=4)
    os.replace(temporaire, chemin)


if __name__ == "__main__":
    chemin = "test_stockage.json"
    if os.path.exists(chemin):
        os.remove(chemin)

    # 1. Premier lancement : fichier absent
    centre = charger(chemin)
    print(len(centre.lister_cours()))

    # 2. Sauvegarde puis rechargement
    centre.ajouter_formateur("Louis", "Marie", "Python")
    centre.ajouter_etudiant("Pierre", "Jean")
    centre.ajouter_etudiant("Joseph", "Sarah")
    centre.creer_cours("Python", 1, 1, [("Lundi", 8, 10)])
    centre.inscrire(1, 1)
    centre.inscrire(2, 1)                 # cours plein : liste d'attente
    centre.creer_evaluation(1, "Examen", 3)
    centre.enregistrer_note(1, 1, 80)
    sauvegarder(centre, chemin)

    centre2 = charger(chemin)
    print(centre2.get_cours(1).description())
    print(centre2.get_cours(1).get_liste_attente())
    print(centre2.moyenne_etudiant_cours(1, 1))
    print(type(centre2.get_formateur(1)).__name__)
    print(len(centre2.get_historique()))

    # 3. Pas de doublon d'identifiant après redémarrage
    nouveau = centre2.ajouter_etudiant("Duval", "David")
    print(nouveau.get_id())

    # 4. Données cohérentes en apparence mais fausses
    data = centre2.to_dict()
    data["cours"][0]["inscrits"].append(999)
    try:
        Centre.depuis_dict(data)
    except ValueError as erreur:
        print("Incohérent :", erreur)

    # 5. Fichier cassé : refusé, et surtout pas écrasé
    with open(chemin, "w", encoding="utf-8") as fichier:
        fichier.write('{"etudiants": [')
    try:
        charger(chemin)
    except FichierInvalideError as erreur:
        print("Refusé :", erreur)
    with open(chemin, "r", encoding="utf-8") as fichier:
        print(fichier.read())

    os.remove(chemin)
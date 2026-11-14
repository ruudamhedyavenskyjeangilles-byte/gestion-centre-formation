import math
import os
import sys
import unicodedata

from centre import SEUIL_REUSSITE
from cours import creneaux_en_conflit
from evaluation import NOTE_MAX
from stockage import NOM_FICHIER, FichierInvalideError, charger, sauvegarder

JOURS = ["Lundi", "Mardi", "Mercredi", "Jeudi", "Vendredi", "Samedi", "Dimanche"]


# ======================================================================
# Saisies contrôlées
# ======================================================================
def lire_texte(message):
    while True:
        texte = input(message).strip()
        if texte != "":
            return texte
        print("Erreur : ce champ ne peut pas être vide.")


def lire_entier(message, minimum=None, maximum=None):
    while True:
        saisie = input(message).strip()
        try:
            valeur = int(saisie)
        except ValueError:
            print("Erreur : veuillez saisir un nombre entier.")
            continue
        if minimum is not None and valeur < minimum:
            print(f"Erreur : la valeur doit être au moins {minimum}.")
        elif maximum is not None and valeur > maximum:
            print(f"Erreur : la valeur doit être au plus {maximum}.")
        else:
            return valeur


def lire_nombre(message, minimum=None, maximum=None):
    """Lit un nombre décimal fini (la virgule est acceptée)."""
    while True:
        saisie = input(message).strip().replace(",", ".")
        try:
            valeur = float(saisie)
        except ValueError:
            print("Erreur : veuillez saisir un nombre (ex : 12 ou 12.5).")
            continue
        if not math.isfinite(valeur):
            print("Erreur : veuillez saisir un nombre valide.")
            continue
        if minimum is not None and valeur < minimum:
            print(f"Erreur : la valeur doit être au moins {minimum}.")
        elif maximum is not None and valeur > maximum:
            print(f"Erreur : la valeur doit être au plus {maximum}.")
        else:
            if valeur == int(valeur):
                valeur = int(valeur)
            return valeur


def lire_jour():
    for numero, jour in enumerate(JOURS, start=1):
        print(f"  {numero} - {jour}")
    return JOURS[lire_entier("  Jour : ", 1, len(JOURS)) - 1]


def lire_creneaux():
    nombre = lire_entier("Nombre de créneaux par semaine : ", 1, 14)
    creneaux = []
    for numero in range(1, nombre + 1):
        print(f"Créneau {numero} :")
        while True:
            jour = lire_jour()
            debut = lire_nombre("  Heure de début (ex : 8 ou 8.5) : ", 0, 24)
            fin = lire_nombre("  Heure de fin : ", 0, 24)
            nouveau = (jour, debut, fin)
            if debut >= fin:
                print("Erreur : l'heure de début doit précéder l'heure de fin.")
            elif any(creneaux_en_conflit(nouveau, c) for c in creneaux):
                print("Erreur : ce créneau chevauche un autre créneau du même cours.")
            else:
                creneaux.append(nouveau)
                break
    return creneaux


# ======================================================================
# Affichage
# ======================================================================
def afficher_titre(texte):
    print()
    print(f"====== {texte} ======")
    print()


def formater_heure(heure):
    heures = int(heure)
    minutes = round((heure - heures) * 60)
    if minutes == 60:
        heures += 1
        minutes = 0
    if minutes == 0:
        return f"{heures}h"
    return f"{heures}h{minutes:02d}"


def formater_creneaux(creneaux):
    morceaux = []
    for jour, debut, fin in creneaux:
        morceaux.append(f"{jour} {formater_heure(debut)}-{formater_heure(fin)}")
    return ", ".join(morceaux)


def formater_moyenne(moyenne):
    if moyenne is None:
        return "N/A"
    return f"{moyenne:.2f}"


def statut(moyenne):
    if moyenne is None:
        return "N/A"
    if moyenne >= SEUIL_REUSSITE:
        return "Réussi"
    return "Échoué"


def normaliser(texte):
    """Minuscules et sans accents, pour des recherches tolérantes."""
    decompose = unicodedata.normalize("NFD", texte.lower())
    return "".join(c for c in decompose if unicodedata.category(c) != "Mn")


def correspond(recherche, *champs):
    """Vrai si tous les mots de la recherche apparaissent dans les champs."""
    cible = normaliser(" ".join(champs))
    for mot in normaliser(recherche).split():
        if mot not in cible:
            return False
    return True


def cle_moyenne_decroissante(paire):
    """Clé de tri pour des paires (objet, moyenne) : meilleures moyennes
    d'abord, absence de moyenne à la fin."""
    moyenne = paire[1]
    if moyenne is None:
        return (1, 0)
    return (0, -moyenne)


def executer_menu(titre_menu, options, libelle_zero="Retour"):
    """Affiche un menu en boucle. options : liste de (libellé, action).
    Toute ValueError levée par une action est affichée sans quitter."""
    while True:
        afficher_titre(titre_menu)
        for numero, (libelle, action) in enumerate(options, start=1):
            print(f"{numero} - {libelle}")
        print(f"0 - {libelle_zero}")
        print()
        choix = lire_entier("Votre choix : ", 0, len(options))
        if choix == 0:
            return
        print()
        try:
            options[choix - 1][1]()
        except ValueError as erreur:
            print("Erreur :", erreur)


# ======================================================================
# Application
# ======================================================================
class Application:
    def __init__(self, centre, chemin):
        self.centre = centre
        self.chemin = chemin

    # ---------- utilitaires ----------
    def enregistrer_donnees(self):
        """Sauvegarde après chaque modification réussie."""
        try:
            sauvegarder(self.centre, self.chemin)
        except OSError as erreur:
            print(f"Attention : la sauvegarde a échoué ({erreur}).")

    def ligne_cours(self, cours):
        formateur = self.centre.get_formateur(cours.get_id_formateur())
        return (f"{cours.description()} | {formateur.get_nom_complet()} | "
                f"{formater_creneaux(cours.get_creneaux())}")

    def afficher_etudiants_courts(self):
        etudiants = self.centre.lister_etudiants()
        if len(etudiants) == 0:
            raise ValueError("Aucun étudiant enregistré.")
        print("Étudiants :")
        for etudiant in etudiants:
            print("  ", etudiant.description())

    def afficher_cours_courts(self):
        liste = self.centre.lister_cours()
        if len(liste) == 0:
            raise ValueError("Aucun cours enregistré.")
        print("Cours :")
        for cours in liste:
            print("  ", self.ligne_cours(cours))

    def afficher_evaluations_courtes(self):
        lignes = []
        for cours in self.centre.lister_cours():
            for evaluation in self.centre.evaluations_du_cours(cours.get_id()):
                lignes.append(f"{evaluation.description()} - cours : {cours.get_titre()}")
        if len(lignes) == 0:
            raise ValueError("Aucune évaluation enregistrée.")
        print("Évaluations :")
        for ligne in lignes:
            print("  ", ligne)

    def etudiants_avec_moyenne(self):
        paires = []
        for etudiant in self.centre.lister_etudiants():
            moyenne = self.centre.moyenne_generale_etudiant(etudiant.get_id())
            paires.append((etudiant, moyenne))
        return paires

    # ---------- étudiants ----------
    def menu_etudiants(self):
        executer_menu("ÉTUDIANTS", [
            ("Ajouter un étudiant", self.ajouter_etudiant),
            ("Lister les étudiants (avec tri)", self.lister_etudiants),
            ("Rechercher un étudiant", self.rechercher_etudiants)
        ])

    def ajouter_etudiant(self):
        nom = lire_texte("Nom : ")
        prenom = lire_texte("Prénom : ")
        etudiant = self.centre.ajouter_etudiant(nom, prenom)
        self.enregistrer_donnees()
        print(f"Étudiant ajouté : {etudiant.description()}")

    def lister_etudiants(self):
        etudiants = self.centre.lister_etudiants()
        if len(etudiants) == 0:
            raise ValueError("Aucun étudiant enregistré.")
        print("Trier par :")
        print("  1 - identifiant")
        print("  2 - nom")
        print("  3 - moyenne générale (décroissante)")
        critere = lire_entier("Votre choix : ", 1, 3)
        print()
        if critere == 1:
            etudiants.sort(key=lambda e: e.get_id())
            for etudiant in etudiants:
                print(etudiant.description())
        elif critere == 2:
            etudiants.sort(key=lambda e: normaliser(e.get_nom() + " " + e.get_prenom()))
            for etudiant in etudiants:
                print(etudiant.description())
        else:
            paires = sorted(self.etudiants_avec_moyenne(), key=cle_moyenne_decroissante)
            for etudiant, moyenne in paires:
                print(f"{etudiant.description()} - moyenne générale : "
                      f"{formater_moyenne(moyenne)}")

    def rechercher_etudiants(self):
        recherche = lire_texte("Nom ou prénom à rechercher : ")
        trouves = [e for e in self.centre.lister_etudiants()
                   if correspond(recherche, e.get_nom(), e.get_prenom())]
        print()
        if len(trouves) == 0:
            print("Aucun étudiant trouvé.")
        for etudiant in trouves:
            print(etudiant.description())

    # ---------- formateurs ----------
    def menu_formateurs(self):
        executer_menu("FORMATEURS", [
            ("Ajouter un formateur", self.ajouter_formateur),
            ("Lister les formateurs", self.lister_formateurs),
            ("Rechercher un formateur", self.rechercher_formateurs)
        ])

    def ajouter_formateur(self):
        nom = lire_texte("Nom : ")
        prenom = lire_texte("Prénom : ")
        specialite = lire_texte("Spécialité : ")
        formateur = self.centre.ajouter_formateur(nom, prenom, specialite)
        self.enregistrer_donnees()
        print(f"Formateur ajouté : {formateur.description()}")

    def lister_formateurs(self):
        formateurs = self.centre.lister_formateurs()
        if len(formateurs) == 0:
            raise ValueError("Aucun formateur enregistré.")
        formateurs.sort(key=lambda f: normaliser(f.get_nom() + " " + f.get_prenom()))
        for formateur in formateurs:
            print(formateur.description())

    def rechercher_formateurs(self):
        recherche = lire_texte("Nom, prénom ou spécialité à rechercher : ")
        trouves = [f for f in self.centre.lister_formateurs()
                   if correspond(recherche, f.get_nom(), f.get_prenom(),
                                 f.get_specialite())]
        print()
        if len(trouves) == 0:
            print("Aucun formateur trouvé.")
        for formateur in trouves:
            print(formateur.description())

    # ---------- cours ----------
    def menu_cours(self):
        executer_menu("COURS", [
            ("Créer un cours", self.creer_cours),
            ("Lister les cours (avec tri)", self.lister_cours),
            ("Rechercher un cours", self.rechercher_cours),
            ("Détails d'un cours", self.details_cours)
        ])

    def creer_cours(self):
        formateurs = self.centre.lister_formateurs()
        if len(formateurs) == 0:
            raise ValueError("Ajoutez d'abord un formateur.")
        titre = lire_texte("Titre du cours : ")
        print("Formateurs :")
        for formateur in formateurs:
            print("  ", formateur.description())
        id_formateur = lire_entier("Identifiant du formateur : ", 1)
        capacite = lire_entier("Capacité (nombre de places) : ", 1)
        creneaux = lire_creneaux()
        cours = self.centre.creer_cours(titre, id_formateur, capacite, creneaux)
        self.enregistrer_donnees()
        print(f"Cours créé : {self.ligne_cours(cours)}")

    def lister_cours(self):
        liste = self.centre.lister_cours()
        if len(liste) == 0:
            raise ValueError("Aucun cours enregistré.")
        print("Trier par :")
        print("  1 - identifiant")
        print("  2 - titre")
        print("  3 - taux de remplissage (décroissant)")
        critere = lire_entier("Votre choix : ", 1, 3)
        if critere == 1:
            liste.sort(key=lambda c: c.get_id())
        elif critere == 2:
            liste.sort(key=lambda c: normaliser(c.get_titre()))
        else:
            liste.sort(key=lambda c: -self.centre.taux_remplissage_cours(c.get_id()))
        print()
        for cours in liste:
            print(self.ligne_cours(cours))

    def rechercher_cours(self):
        recherche = lire_texte("Titre à rechercher : ")
        trouves = [c for c in self.centre.lister_cours()
                   if correspond(recherche, c.get_titre())]
        print()
        if len(trouves) == 0:
            print("Aucun cours trouvé.")
        for cours in trouves:
            print(self.ligne_cours(cours))

    def details_cours(self):
        self.afficher_cours_courts()
        id_cours = lire_entier("Identifiant du cours : ", 1)
        cours = self.centre.get_cours(id_cours)
        print()
        print(self.ligne_cours(cours))
        print(f"Places restantes : {cours.places_restantes()}")
        print("Inscrits :")
        if len(cours.get_inscrits()) == 0:
            print("   (aucun)")
        for id_etudiant in cours.get_inscrits():
            print("  ", self.centre.get_etudiant(id_etudiant).get_nom_complet())
        print("Liste d'attente :")
        if len(cours.get_liste_attente()) == 0:
            print("   (aucune)")
        for rang, id_etudiant in enumerate(cours.get_liste_attente(), start=1):
            print(f"   {rang}. {self.centre.get_etudiant(id_etudiant).get_nom_complet()}")

    # ---------- inscriptions ----------
    def menu_inscriptions(self):
        executer_menu("INSCRIPTIONS", [
            ("Inscrire un étudiant à un cours", self.inscrire),
            ("Désinscrire un étudiant d'un cours", self.desinscrire)
        ])

    def inscrire(self):
        self.afficher_etudiants_courts()
        id_etudiant = lire_entier("Identifiant de l'étudiant : ", 1)
        self.afficher_cours_courts()
        id_cours = lire_entier("Identifiant du cours : ", 1)
        resultat = self.centre.inscrire(id_etudiant, id_cours)
        self.enregistrer_donnees()
        if resultat == "inscrit":
            print("Inscription confirmée.")
        else:
            rang = len(self.centre.get_cours(id_cours).get_liste_attente())
            print(f"Le cours est plein : l'étudiant est placé en liste d'attente "
                  f"(position {rang}).")

    def desinscrire(self):
        self.afficher_etudiants_courts()
        id_etudiant = lire_entier("Identifiant de l'étudiant : ", 1)
        self.afficher_cours_courts()
        id_cours = lire_entier("Identifiant du cours : ", 1)
        promu = self.centre.desinscrire(id_etudiant, id_cours)
        self.enregistrer_donnees()
        print("Désinscription effectuée.")
        if promu is not None:
            nom = self.centre.get_etudiant(promu).get_nom_complet()
            print(f"Une place s'est libérée : {nom} a été inscrit(e) depuis "
                  f"la liste d'attente.")

    # ---------- évaluations et notes ----------
    def menu_evaluations(self):
        executer_menu("ÉVALUATIONS ET NOTES", [
            ("Créer une évaluation", self.creer_evaluation),
            ("Enregistrer une note", self.enregistrer_note),
            ("Voir les évaluations d'un cours", self.voir_evaluations)
        ])

    def creer_evaluation(self):
        self.afficher_cours_courts()
        id_cours = lire_entier("Identifiant du cours : ", 1)
        titre = lire_texte("Titre de l'évaluation : ")
        while True:
            coefficient = lire_nombre("Coefficient (supérieur à 0) : ")
            if coefficient > 0:
                break
            print("Erreur : le coefficient doit être supérieur à 0.")
        evaluation = self.centre.creer_evaluation(id_cours, titre, coefficient)
        self.enregistrer_donnees()
        print(f"Évaluation créée : {evaluation.description()}")

    def enregistrer_note(self):
        self.afficher_evaluations_courtes()
        id_evaluation = lire_entier("Identifiant de l'évaluation : ", 1)
        evaluation = self.centre.get_evaluation(id_evaluation)
        cours = self.centre.get_cours(evaluation.get_id_cours())
        if len(cours.get_inscrits()) == 0:
            raise ValueError("Aucun étudiant n'est inscrit à ce cours.")
        print("Étudiants inscrits :")
        for id_etudiant in cours.get_inscrits():
            print("  ", self.centre.get_etudiant(id_etudiant).description())
        id_etudiant = lire_entier("Identifiant de l'étudiant : ", 1)
        note = lire_nombre(f"Note (0 à {NOTE_MAX}) : ", 0, NOTE_MAX)
        self.centre.enregistrer_note(id_evaluation, id_etudiant, note)
        self.enregistrer_donnees()
        print("Note enregistrée.")

    def voir_evaluations(self):
        self.afficher_cours_courts()
        id_cours = lire_entier("Identifiant du cours : ", 1)
        cours = self.centre.get_cours(id_cours)
        evaluations = self.centre.evaluations_du_cours(id_cours)
        print()
        if len(evaluations) == 0:
            print("Aucune évaluation pour ce cours.")
            return
        for evaluation in evaluations:
            print(evaluation.description())
            for id_etudiant in cours.get_inscrits():
                note = evaluation.get_note(id_etudiant)
                texte = "note manquante" if note is None else str(note)
                nom = self.centre.get_etudiant(id_etudiant).get_nom_complet()
                print(f"     {nom} : {texte}")

    # ---------- résultats et statistiques ----------
    def menu_resultats(self):
        executer_menu("RÉSULTATS ET STATISTIQUES", [
            ("Résultats d'un étudiant", self.resultats_etudiant),
            ("Statistiques d'un cours", self.statistiques_cours),
            ("Classement des étudiants (moyenne générale)", self.classement_etudiants),
            ("Remplissage des cours", self.remplissage_cours)
        ])

    def resultats_etudiant(self):
        self.afficher_etudiants_courts()
        id_etudiant = lire_entier("Identifiant de l'étudiant : ", 1)
        etudiant = self.centre.get_etudiant(id_etudiant)
        afficher_titre(f"Résultats : {etudiant.get_nom_complet()}")
        ids_cours = etudiant.get_cours_inscrits()
        if len(ids_cours) == 0:
            print("Cet étudiant n'est inscrit à aucun cours.")
            return
        for id_cours in ids_cours:
            cours = self.centre.get_cours(id_cours)
            print(f"Cours : {cours.get_titre()}")
            for evaluation in self.centre.evaluations_du_cours(id_cours):
                note = evaluation.get_note(id_etudiant)
                texte = "note manquante" if note is None else str(note)
                print(f"   {evaluation.get_titre()} "
                      f"(coef. {evaluation.get_coefficient()}) : {texte}")
            moyenne = self.centre.moyenne_etudiant_cours(id_etudiant, id_cours)
            print(f"   Moyenne : {formater_moyenne(moyenne)} - {statut(moyenne)}")
            print()
        general = self.centre.moyenne_generale_etudiant(id_etudiant)
        print(f"Moyenne générale : {formater_moyenne(general)}")

    def statistiques_cours(self):
        self.afficher_cours_courts()
        id_cours = lire_entier("Identifiant du cours : ", 1)
        cours = self.centre.get_cours(id_cours)
        formateur = self.centre.get_formateur(cours.get_id_formateur())
        afficher_titre(f"Statistiques : {cours.get_titre()}")
        print(f"Formateur : {formateur.get_nom_complet()}")
        print(f"Inscrits : {len(cours.get_inscrits())}/{cours.get_capacite()}")
        print(f"Liste d'attente : {len(cours.get_liste_attente())}")
        remplissage = self.centre.taux_remplissage_cours(id_cours)
        print(f"Taux de remplissage : {remplissage:.1f} %")
        taux = self.centre.taux_reussite_cours(id_cours)
        texte_taux = "N/A" if taux is None else f"{taux:.1f} %"
        print(f"Taux de réussite : {texte_taux}")

        classement = []
        for id_etudiant in cours.get_inscrits():
            moyenne = self.centre.moyenne_etudiant_cours(id_etudiant, id_cours)
            classement.append((self.centre.get_etudiant(id_etudiant), moyenne))
        classement.sort(key=cle_moyenne_decroissante)
        if len(classement) > 0:
            print()
            print("Résultats des étudiants :")
            for rang, (etudiant, moyenne) in enumerate(classement, start=1):
                print(f"   {rang}. {etudiant.get_nom_complet()} : "
                      f"{formater_moyenne(moyenne)} - {statut(moyenne)}")
            moyennes = [m for _, m in classement if m is not None]
            if len(moyennes) > 0:
                print(f"Moyenne du cours : {sum(moyennes) / len(moyennes):.2f}")

    def classement_etudiants(self):
        paires = sorted(self.etudiants_avec_moyenne(), key=cle_moyenne_decroissante)
        if len(paires) == 0:
            raise ValueError("Aucun étudiant enregistré.")
        for rang, (etudiant, moyenne) in enumerate(paires, start=1):
            print(f"{rang}. {etudiant.get_nom_complet()} : "
                  f"{formater_moyenne(moyenne)} - {statut(moyenne)}")

    def remplissage_cours(self):
        liste = self.centre.lister_cours()
        if len(liste) == 0:
            raise ValueError("Aucun cours enregistré.")
        liste.sort(key=lambda c: -self.centre.taux_remplissage_cours(c.get_id()))
        for cours in liste:
            taux = self.centre.taux_remplissage_cours(cours.get_id())
            print(f"{cours.get_titre()} : {len(cours.get_inscrits())}/"
                  f"{cours.get_capacite()} ({taux:.1f} %) - "
                  f"{len(cours.get_liste_attente())} en attente")

    # ---------- historique ----------
    def menu_historique(self):
        executer_menu("HISTORIQUE", [
            ("Afficher tout l'historique", lambda: self.afficher_historique()),
            ("Afficher les 10 dernières opérations", lambda: self.afficher_historique(10))
        ])

    def afficher_historique(self, limite=None):
        historique = self.centre.get_historique()
        if limite is not None:
            historique = historique[-limite:]
        if len(historique) == 0:
            print("L'historique est vide.")
            return
        for entree in historique:
            print(f"[{entree['date']}] {entree['operation']} : {entree['details']}")

    # ---------- menu principal ----------
    def lancer(self):
        executer_menu("CENTRE DE FORMATION", [
            ("Étudiants", self.menu_etudiants),
            ("Formateurs", self.menu_formateurs),
            ("Cours", self.menu_cours),
            ("Inscriptions", self.menu_inscriptions),
            ("Évaluations et notes", self.menu_evaluations),
            ("Résultats et statistiques", self.menu_resultats),
            ("Historique", self.menu_historique)
        ], "Quitter")
        print()
        print("Au revoir !")


def main():
    chemin = NOM_FICHIER
    if len(sys.argv) > 1:
        chemin = sys.argv[1]

    existait = os.path.exists(chemin)
    try:
        centre = charger(chemin)
    except FichierInvalideError as erreur:
        print("ERREUR :", erreur)
        print("Le programme s'arrête pour ne pas écraser ce fichier.")
        print("Corrigez-le ou déplacez-le, puis relancez le programme.")
        sys.exit(1)

    if existait:
        print(f"Données chargées depuis {chemin}.")
    else:
        print(f"Aucun fichier {chemin} trouvé : un nouveau centre vide est créé.")

    application = Application(centre, chemin)
    try:
        application.lancer()
    except (KeyboardInterrupt, EOFError):
        print()
        print("Programme interrompu. Les opérations déjà validées sont sauvegardées.")


if __name__ == "__main__":
    main()

from datetime import datetime

from personne import Etudiant, Formateur
from cours import Cours
from evaluation import Evaluation

SEUIL_REUSSITE = 60    # moyenne minimale pour réussir un cours (sur 100)


class Centre:
    def __init__(self):
        self._etudiants = {}      # id -> Etudiant
        self._formateurs = {}     # id -> Formateur
        self._cours = {}          # id -> Cours
        self._evaluations = {}    # id -> Evaluation
        self._historique = []     # liste de dictionnaires

    # ---------- utilitaires ----------
    @staticmethod
    def _prochain_id(dictionnaire):
        """Plus grand identifiant existant + 1 (évite les doublons
        même après un rechargement depuis le JSON)."""
        if len(dictionnaire) == 0:
            return 1
        return max(dictionnaire.keys()) + 1

    def _enregistrer(self, operation, details):
        self._historique.append({
            "date": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "operation": operation,
            "details": details
        })

    def get_historique(self):
        return list(self._historique)

    # ---------- accès aux objets ----------
    def get_etudiant(self, id_etudiant):
        if id_etudiant not in self._etudiants:
            raise ValueError("Étudiant introuvable.")
        return self._etudiants[id_etudiant]

    def get_formateur(self, id_formateur):
        if id_formateur not in self._formateurs:
            raise ValueError("Formateur introuvable.")
        return self._formateurs[id_formateur]

    def get_cours(self, id_cours):
        if id_cours not in self._cours:
            raise ValueError("Cours introuvable.")
        return self._cours[id_cours]

    def get_evaluation(self, id_evaluation):
        if id_evaluation not in self._evaluations:
            raise ValueError("Évaluation introuvable.")
        return self._evaluations[id_evaluation]

    def lister_etudiants(self):
        return list(self._etudiants.values())

    def lister_formateurs(self):
        return list(self._formateurs.values())

    def lister_cours(self):
        return list(self._cours.values())

    def evaluations_du_cours(self, id_cours):
        self.get_cours(id_cours)
        return [e for e in self._evaluations.values()
                if e.get_id_cours() == id_cours]

    # ---------- création ----------
    def ajouter_etudiant(self, nom, prenom):
        nom = nom.strip()
        prenom = prenom.strip()
        if nom == "" or prenom == "":
            raise ValueError("Le nom et le prénom sont obligatoires.")

        etudiant = Etudiant(self._prochain_id(self._etudiants), nom, prenom)
        self._etudiants[etudiant.get_id()] = etudiant
        self._enregistrer("ajout_etudiant",
                          f"Étudiant ajouté : {etudiant.get_nom_complet()}")
        return etudiant

    def ajouter_formateur(self, nom, prenom, specialite):
        nom = nom.strip()
        prenom = prenom.strip()
        specialite = specialite.strip()
        if nom == "" or prenom == "" or specialite == "":
            raise ValueError("Le nom, le prénom et la spécialité sont obligatoires.")

        formateur = Formateur(self._prochain_id(self._formateurs),
                              nom, prenom, specialite)
        self._formateurs[formateur.get_id()] = formateur
        self._enregistrer("ajout_formateur",
                          f"Formateur ajouté : {formateur.get_nom_complet()}")
        return formateur

    def creer_cours(self, titre, id_formateur, capacite, creneaux):
        formateur = self.get_formateur(id_formateur)
        titre = titre.strip()
        if titre == "":
            raise ValueError("Le titre du cours est obligatoire.")

        # Le constructeur valide la capacité et les créneaux
        cours = Cours(self._prochain_id(self._cours), titre,
                      id_formateur, capacite, creneaux)

        # Le formateur ne doit pas avoir un autre cours au même moment
        for id_autre in formateur.get_cours_animes():
            if cours.a_conflit_avec(self._cours[id_autre].get_creneaux()):
                raise ValueError(
                    "Le formateur a déjà un cours qui chevauche ces créneaux.")

        # Tout est valide : on peut modifier les données
        self._cours[cours.get_id()] = cours
        formateur.ajouter_cours_anime(cours.get_id())
        self._enregistrer("creation_cours",
                          f"Cours créé : {titre} (formateur : "
                          f"{formateur.get_nom_complet()})")
        return cours

    # ---------- inscriptions ----------
    def _creneaux_etudiant(self, etudiant):
        """Tous les créneaux des cours auxquels l'étudiant est inscrit."""
        creneaux = []
        for id_cours in etudiant.get_cours_inscrits():
            creneaux.extend(self._cours[id_cours].get_creneaux())
        return creneaux

    def inscrire(self, id_etudiant, id_cours):
        """Retourne "inscrit" ou "attente". Lève ValueError si refusé,
        sans rien modifier."""
        etudiant = self.get_etudiant(id_etudiant)
        cours = self.get_cours(id_cours)

        # 1. Toutes les vérifications d'abord
        if cours.est_inscrit(id_etudiant):
            raise ValueError("L'étudiant est déjà inscrit à ce cours.")
        if cours.est_en_attente(id_etudiant):
            raise ValueError("L'étudiant est déjà en liste d'attente pour ce cours.")
        if cours.a_conflit_avec(self._creneaux_etudiant(etudiant)):
            raise ValueError(
                "Conflit d'horaire avec un cours déjà suivi par l'étudiant.")

        # 2. Ensuite seulement, on modifie les données
        if cours.est_plein():
            cours.ajouter_attente(id_etudiant)
            self._enregistrer("attente",
                              f"{etudiant.get_nom_complet()} mis en liste "
                              f"d'attente du cours {cours.get_titre()}")
            return "attente"

        cours.ajouter_inscrit(id_etudiant)
        etudiant.ajouter_cours(id_cours)
        self._enregistrer("inscription",
                          f"{etudiant.get_nom_complet()} inscrit au cours "
                          f"{cours.get_titre()}")
        return "inscrit"

    def desinscrire(self, id_etudiant, id_cours):
        """Retire l'étudiant du cours (ou de sa liste d'attente).
        Retourne l'identifiant de l'étudiant promu depuis la liste
        d'attente, ou None si personne n'a été promu."""
        etudiant = self.get_etudiant(id_etudiant)
        cours = self.get_cours(id_cours)

        if cours.est_en_attente(id_etudiant):
            cours.retirer_attente(id_etudiant)
            self._enregistrer("retrait_attente",
                              f"{etudiant.get_nom_complet()} retiré de la liste "
                              f"d'attente du cours {cours.get_titre()}")
            return None

        if not cours.est_inscrit(id_etudiant):
            raise ValueError(
                "L'étudiant n'est ni inscrit ni en liste d'attente pour ce cours.")

        cours.retirer_inscrit(id_etudiant)
        etudiant.retirer_cours(id_cours)
        self._supprimer_notes(id_etudiant, id_cours)
        self._enregistrer("desinscription",
                          f"{etudiant.get_nom_complet()} retiré du cours "
                          f"{cours.get_titre()}")

        return self._promouvoir_depuis_attente(cours)

    def _promouvoir_depuis_attente(self, cours):
        """Attribue la place libérée au premier candidat admissible
        (sans conflit d'horaire). Les candidats non admissibles restent
        dans la liste, à leur rang."""
        for id_candidat in cours.get_liste_attente():
            candidat = self._etudiants[id_candidat]
            if not cours.a_conflit_avec(self._creneaux_etudiant(candidat)):
                cours.retirer_attente(id_candidat)
                cours.ajouter_inscrit(id_candidat)
                candidat.ajouter_cours(cours.get_id())
                self._enregistrer("promotion",
                                  f"{candidat.get_nom_complet()} promu depuis la "
                                  f"liste d'attente du cours {cours.get_titre()}")
                return id_candidat
        return None

    # ---------- évaluations et notes ----------
    def creer_evaluation(self, id_cours, titre, coefficient):
        cours = self.get_cours(id_cours)

        # Le constructeur valide le titre et le coefficient
        evaluation = Evaluation(self._prochain_id(self._evaluations),
                                id_cours, titre, coefficient)

        self._evaluations[evaluation.get_id()] = evaluation
        self._enregistrer("creation_evaluation",
                          f"Évaluation « {evaluation.get_titre()} » "
                          f"(coef. {coefficient}) créée pour le cours "
                          f"{cours.get_titre()}")
        return evaluation

    def enregistrer_note(self, id_evaluation, id_etudiant, note):
        evaluation = self.get_evaluation(id_evaluation)
        etudiant = self.get_etudiant(id_etudiant)
        cours = self.get_cours(evaluation.get_id_cours())

        if not cours.est_inscrit(id_etudiant):
            raise ValueError(
                "L'étudiant n'est pas inscrit au cours de cette évaluation.")

        # Valide la note puis l'enregistre
        evaluation.enregistrer_note(id_etudiant, note)
        self._enregistrer("note",
                          f"Note {note} enregistrée pour "
                          f"{etudiant.get_nom_complet()} "
                          f"({evaluation.get_titre()}, cours {cours.get_titre()})")

    def _supprimer_notes(self, id_etudiant, id_cours):
        for evaluation in self.evaluations_du_cours(id_cours):
            evaluation.supprimer_note(id_etudiant)

    # ---------- moyennes et indicateurs ----------
    def moyenne_etudiant_cours(self, id_etudiant, id_cours):
        """Moyenne pondérée sur les évaluations notées uniquement.
        Une note manquante est ignorée (son coefficient aussi).
        Retourne None si l'étudiant n'a aucune note dans ce cours."""
        somme = 0
        total_coefficients = 0
        for evaluation in self.evaluations_du_cours(id_cours):
            note = evaluation.get_note(id_etudiant)
            if note is not None:
                somme += note * evaluation.get_coefficient()
                total_coefficients += evaluation.get_coefficient()

        if total_coefficients == 0:
            return None
        return somme / total_coefficients

    def moyenne_generale_etudiant(self, id_etudiant):
        """Moyenne des moyennes de ses cours (cours sans note ignorés)."""
        etudiant = self.get_etudiant(id_etudiant)
        moyennes = []
        for id_cours in etudiant.get_cours_inscrits():
            moyenne = self.moyenne_etudiant_cours(id_etudiant, id_cours)
            if moyenne is not None:
                moyennes.append(moyenne)

        if len(moyennes) == 0:
            return None
        return sum(moyennes) / len(moyennes)

    def taux_reussite_cours(self, id_cours):
        """Pourcentage d'étudiants ayant une moyenne >= SEUIL_REUSSITE,
        parmi ceux qui ont au moins une note. None si personne n'a de note."""
        cours = self.get_cours(id_cours)
        avec_moyenne = 0
        reussis = 0
        for id_etudiant in cours.get_inscrits():
            moyenne = self.moyenne_etudiant_cours(id_etudiant, id_cours)
            if moyenne is not None:
                avec_moyenne += 1
                if moyenne >= SEUIL_REUSSITE:
                    reussis += 1

        if avec_moyenne == 0:
            return None
        return reussis / avec_moyenne * 100

    def taux_remplissage_cours(self, id_cours):
        cours = self.get_cours(id_cours)
        return len(cours.get_inscrits()) / cours.get_capacite() * 100


if __name__ == "__main__":
    centre = Centre()
    centre.ajouter_formateur("Louis", "Marie", "Python")     # id 1
    centre.ajouter_etudiant("Pierre", "Jean")                # id 1
    centre.ajouter_etudiant("Joseph", "Sarah")               # id 2
    centre.ajouter_etudiant("Duval", "David")                # id 3
    centre.ajouter_etudiant("Charles", "Esther")             # id 4 (non inscrite)
    centre.creer_cours("Python", 1, 3, [("Lundi", 8, 10)])   # id 1

    centre.inscrire(1, 1)
    centre.inscrire(2, 1)
    centre.inscrire(3, 1)

    centre.creer_evaluation(1, "Examen", 3)                  # id 1
    centre.creer_evaluation(1, "TP", 1)                      # id 2

    centre.enregistrer_note(1, 1, 80)    # Jean   : Examen 80
    centre.enregistrer_note(2, 1, 60)    # Jean   : TP 60
    centre.enregistrer_note(1, 2, 50)    # Sarah  : Examen 50 (pas de TP)
                                         # David  : aucune note

    print(centre.moyenne_etudiant_cours(1, 1))   # 75.0
    print(centre.moyenne_etudiant_cours(2, 1))   # 50.0
    print(centre.moyenne_etudiant_cours(3, 1))   # None

    for id_eval, id_etudiant, note in [(1, 1, 150), (1, 4, 70)]:
        try:
            centre.enregistrer_note(id_eval, id_etudiant, note)
        except ValueError as erreur:
            print("Refusé :", erreur)

    print(centre.taux_reussite_cours(1))         # 50.0
    print(centre.taux_remplissage_cours(1))      # 100.0
    print(centre.moyenne_generale_etudiant(1))   # 75.0

    centre.desinscrire(1, 1)                     # supprime aussi ses notes
    print(centre.moyenne_etudiant_cours(1, 1))   # None
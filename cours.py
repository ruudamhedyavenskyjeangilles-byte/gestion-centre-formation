def creneaux_en_conflit(c1, c2):
    """Deux créneaux (jour, debut, fin) sont en conflit s'ils ont lieu
    le même jour et se chevauchent. Un créneau qui commence quand
    l'autre finit n'est PAS un conflit."""
    jour1, debut1, fin1 = c1
    jour2, debut2, fin2 = c2
    return jour1 == jour2 and debut1 < fin2 and debut2 < fin1


class Cours:
    def __init__(self, id_cours, titre, id_formateur, capacite, creneaux):
        if capacite <= 0:
            raise ValueError("La capacité doit être supérieure à 0.")
        if len(creneaux) == 0:
            raise ValueError("Un cours doit avoir au moins un créneau.")
        for jour, debut, fin in creneaux:
            if debut >= fin:
                raise ValueError("Le début d'un créneau doit précéder sa fin.")

        self._id = id_cours
        self._titre = titre
        self._id_formateur = id_formateur
        self._capacite = capacite
        self._creneaux = list(creneaux)   # liste de tuples (jour, debut, fin)
        self._inscrits = []               # identifiants des étudiants
        self._liste_attente = []          # identifiants, dans l'ordre d'arrivée

    def get_id(self):
        return self._id

    def get_titre(self):
        return self._titre

    def get_id_formateur(self):
        return self._id_formateur

    def get_capacite(self):
        return self._capacite

    def get_creneaux(self):
        return list(self._creneaux)

    def get_inscrits(self):
        return list(self._inscrits)

    def get_liste_attente(self):
        return list(self._liste_attente)

    def est_plein(self):
        return len(self._inscrits) >= self._capacite

    def places_restantes(self):
        return self._capacite - len(self._inscrits)

    def est_inscrit(self, id_etudiant):
        return id_etudiant in self._inscrits

    def est_en_attente(self, id_etudiant):
        return id_etudiant in self._liste_attente

    def ajouter_inscrit(self, id_etudiant):
        if self.est_inscrit(id_etudiant):
            raise ValueError("L'étudiant est déjà inscrit à ce cours.")
        if self.est_plein():
            raise ValueError("Le cours est plein.")
        self._inscrits.append(id_etudiant)

    def retirer_inscrit(self, id_etudiant):
        if not self.est_inscrit(id_etudiant):
            raise ValueError("L'étudiant n'est pas inscrit à ce cours.")
        self._inscrits.remove(id_etudiant)

    def ajouter_attente(self, id_etudiant):
        if self.est_en_attente(id_etudiant):
            raise ValueError("L'étudiant est déjà en liste d'attente.")
        self._liste_attente.append(id_etudiant)

    def retirer_attente(self, id_etudiant):
        if not self.est_en_attente(id_etudiant):
            raise ValueError("L'étudiant n'est pas en liste d'attente.")
        self._liste_attente.remove(id_etudiant)

    def a_conflit_avec(self, autres_creneaux):
        """True si au moins un de mes créneaux chevauche un des autres."""
        for mon_creneau in self._creneaux:
            for autre in autres_creneaux:
                if creneaux_en_conflit(mon_creneau, autre):
                    return True
        return False

    def description(self):
        return (f"[{self._id}] {self._titre} - "
                f"{len(self._inscrits)}/{self._capacite} inscrits")

    def to_dict(self):
        return {
            "id": self._id,
            "titre": self._titre,
            "id_formateur": self._id_formateur,
            "capacite": self._capacite,
            "creneaux": [list(c) for c in self._creneaux],
            "inscrits": list(self._inscrits),
            "liste_attente": list(self._liste_attente)
        }


def cours_depuis_dict(data):
    """Reconstitue un Cours à partir d'un dictionnaire JSON."""
    creneaux = [tuple(c) for c in data["creneaux"]]   # JSON donne des listes
    cours = Cours(data["id"], data["titre"], data["id_formateur"],
                  data["capacite"], creneaux)
    cours._inscrits = list(data["inscrits"])
    cours._liste_attente = list(data["liste_attente"])
    return cours


if __name__ == "__main__":
    c1 = Cours(1, "Python", 10, 2, [("Lundi", 8, 10), ("Mercredi", 14, 16)])
    c1.ajouter_inscrit(100)
    c1.ajouter_inscrit(101)
    print(c1.est_plein())                # True
    c1.ajouter_attente(102)

    copie = cours_depuis_dict(c1.to_dict())
    print(copie.description())           # [1] Python - 2/2 inscrits
    print(copie.get_liste_attente())     # [102]
    print(copie.get_creneaux())          # [('Lundi', 8, 10), ('Mercredi', 14, 16)]
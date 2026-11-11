class Personne:
    def __init__(self, id_personne, nom, prenom):
        self._id = id_personne
        self._nom = nom
        self._prenom = prenom

    def get_id(self):
        return self._id

    def get_nom(self):
        return self._nom

    def get_prenom(self):
        return self._prenom

    def get_nom_complet(self):
        return f"{self._prenom} {self._nom}"

    def description(self):
        return f"[{self._id}] {self.get_nom_complet()}"

    def to_dict(self):
        return {
            "id": self._id,
            "nom": self._nom,
            "prenom": self._prenom
        }


class Etudiant(Personne):
    def __init__(self, id_personne, nom, prenom):
        super().__init__(id_personne, nom, prenom)
        self._cours_inscrits = []   # liste d'identifiants de cours

    def get_cours_inscrits(self):
        return list(self._cours_inscrits)

    def est_inscrit(self, id_cours):
        return id_cours in self._cours_inscrits

    def ajouter_cours(self, id_cours):
        if id_cours not in self._cours_inscrits:
            self._cours_inscrits.append(id_cours)

    def retirer_cours(self, id_cours):
        if id_cours in self._cours_inscrits:
            self._cours_inscrits.remove(id_cours)

    def description(self):
        return f"{super().description()} - {len(self._cours_inscrits)} cours inscrit(s)"

    def to_dict(self):
        data = super().to_dict()
        data["type"] = "etudiant"
        data["cours_inscrits"] = list(self._cours_inscrits)
        return data


class Formateur(Personne):
    def __init__(self, id_personne, nom, prenom, specialite):
        super().__init__(id_personne, nom, prenom)
        self._specialite = specialite
        self._cours_animes = []     # liste d'identifiants de cours

    def get_specialite(self):
        return self._specialite

    def get_cours_animes(self):
        return list(self._cours_animes)

    def ajouter_cours_anime(self, id_cours):
        if id_cours not in self._cours_animes:
            self._cours_animes.append(id_cours)

    def retirer_cours_anime(self, id_cours):
        if id_cours in self._cours_animes:
            self._cours_animes.remove(id_cours)

    def description(self):
        return (f"{super().description()} - Spécialité : {self._specialite}"
                f" - {len(self._cours_animes)} cours animé(s)")

    def to_dict(self):
        data = super().to_dict()
        data["type"] = "formateur"
        data["specialite"] = self._specialite
        data["cours_animes"] = list(self._cours_animes)
        return data


def personne_depuis_dict(data):
    """Reconstitue un Etudiant ou un Formateur à partir d'un dictionnaire JSON."""
    if data["type"] == "etudiant":
        etudiant = Etudiant(data["id"], data["nom"], data["prenom"])
        for id_cours in data.get("cours_inscrits", []):
            etudiant.ajouter_cours(id_cours)
        return etudiant

    if data["type"] == "formateur":
        formateur = Formateur(data["id"], data["nom"], data["prenom"], data["specialite"])
        for id_cours in data.get("cours_animes", []):
            formateur.ajouter_cours_anime(id_cours)
        return formateur

    raise ValueError(f"Type de personne inconnu : {data['type']}")


if __name__ == "__main__":
    e = Etudiant(1, "Pierre", "Jean")
    f = Formateur(2, "Louis", "Marie", "Python")

    e.ajouter_cours(10)
    e.ajouter_cours(10)      # doublon : ignoré
    e.ajouter_cours(11)
    f.ajouter_cours_anime(10)

    for p in [e, f]:
        print(p.description())

    e.retirer_cours(10)
    print(e.get_cours_inscrits())

    d = e.to_dict()
    print(d)

    e2 = personne_depuis_dict(d)
    print(type(e2).__name__, e2.description())

    f2 = personne_depuis_dict(f.to_dict())
    print(type(f2).__name__, f2.description())
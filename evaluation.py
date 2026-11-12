NOTE_MAX = 100


class Evaluation:
    def __init__(self, id_evaluation, id_cours, titre, coefficient):
        if titre.strip() == "":
            raise ValueError("Le titre de l'évaluation est obligatoire.")
        if isinstance(coefficient, bool) or not isinstance(coefficient, (int, float)):
            raise ValueError("Le coefficient doit être un nombre.")
        if coefficient <= 0:
            raise ValueError("Le coefficient doit être supérieur à 0.")

        self._id = id_evaluation
        self._id_cours = id_cours
        self._titre = titre.strip()
        self._coefficient = coefficient
        self._notes = {}      # id_etudiant -> note

    def get_id(self):
        return self._id

    def get_id_cours(self):
        return self._id_cours

    def get_titre(self):
        return self._titre

    def get_coefficient(self):
        return self._coefficient

    def get_notes(self):
        return dict(self._notes)

    def get_note(self, id_etudiant):
        """Retourne la note, ou None si elle est manquante."""
        return self._notes.get(id_etudiant)

    def enregistrer_note(self, id_etudiant, note):
        if isinstance(note, bool) or not isinstance(note, (int, float)):
            raise ValueError("La note doit être un nombre.")
        if note < 0 or note > NOTE_MAX:
            raise ValueError(f"La note doit être comprise entre 0 et {NOTE_MAX}.")
        self._notes[id_etudiant] = note

    def supprimer_note(self, id_etudiant):
        if id_etudiant in self._notes:
            del self._notes[id_etudiant]

    def description(self):
        return (f"[{self._id}] {self._titre} (coef. {self._coefficient}) - "
                f"{len(self._notes)} note(s)")

    def to_dict(self):
        return {
            "id": self._id,
            "id_cours": self._id_cours,
            "titre": self._titre,
            "coefficient": self._coefficient,
            # JSON n'accepte que des clés texte
            "notes": {str(id_etudiant): note
                      for id_etudiant, note in self._notes.items()}
        }


def evaluation_depuis_dict(data):
    evaluation = Evaluation(data["id"], data["id_cours"],
                            data["titre"], data["coefficient"])
    for cle, note in data["notes"].items():
        evaluation.enregistrer_note(int(cle), note)   # on repasse en entier
    return evaluation
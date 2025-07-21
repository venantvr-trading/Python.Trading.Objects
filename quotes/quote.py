import json
import math
from abc import ABC, abstractmethod
from typing import Type


class Quote(ABC):
    """
    Classe abstraite de base pour toutes les devises.

    Gère les montants et applique une précision spécifique.
    """

    # Précisions par défaut pour les classes de devise.
    precisions = {
        "Token": 5,
        "USD": 2
    }

    def __init__(self, amount: float, _from_factory: bool = False):
        """
        Initialise une instance de Quote.

        Paramètres:
        amount (float): Le montant de la devise.
        _from_factory (bool): Interne, indique si l'instance est créée via une factory.
        """
        # La vérification _from_factory est effectuée dans les classes concrètes héritant de Quote.

        child_class = self.get_child_class()
        # Détermine la précision en fonction du nom de la classe fille.
        self.precision = Quote.precisions.get(child_class.__name__, 8 if child_class.__name__ == "Token" else 2)

        self.amount = self.truncate_to_precision(amount)

    def get_child_class(self):
        """Retourne le type de la classe fille de l'instance courante."""
        return self.__class__

    def truncate_to_precision(self, amount: float) -> float:
        """
        Tronque une valeur à la précision définie (sans arrondi).

        Paramètres:
        amount (float): Le montant à tronquer.

        Retourne:
        float: Le montant tronqué.
        """
        bot_assert(amount, (float, int))
        factor = 10 ** self.precision
        truncated_amount = math.floor(amount * factor) / factor
        return float(truncated_amount)

    @staticmethod
    def set_precision(class_name: str, precision: int):
        """
        Définit la précision pour une classe de devise spécifique.

        Paramètres:
        class_name (str): Nom de la classe (ex: "Token", "USD").
        precision (int): La précision numérique à appliquer.
        """
        Quote.precisions[class_name] = precision

    def __eq__(self, other):
        """Vérifie si deux instances de Quote sont égales en montant."""
        bot_assert(other, Quote)
        return self.amount == other.amount

    @abstractmethod
    def __str__(self):
        """Retourne une représentation en chaîne de caractères du montant."""
        pass

    @abstractmethod
    def __lt__(self, other):
        """Vérifie si l'instance courante est inférieure à une autre."""
        pass

    @abstractmethod
    def __add__(self, other):
        """Additionne deux instances."""
        pass

    @abstractmethod
    def __radd__(self, other):
        """Gère la somme lorsque l'instance est à droite de l'opérateur."""
        pass

    @abstractmethod
    def __sub__(self, other):
        """Soustrait une instance d'une autre."""
        pass

    @abstractmethod
    def __neg__(self):
        """Retourne le montant négatif de l'instance."""
        pass

    @abstractmethod
    def __mul__(self, other):
        """Multiplie l'instance par un nombre ou une autre instance de devise/prix."""
        pass

    @abstractmethod
    def __truediv__(self, other):
        """Divise l'instance par un nombre, une autre devise ou un prix."""
        pass

    def to_dict(self):
        """Convertit l'objet en dictionnaire."""
        return dict(price=self.amount)

    def to_json(self):
        """Convertit l'objet en JSON."""
        return json.dumps(self.to_dict())


def bot_assert(variable, instance: Type or tuple[Type]):
    """
    Vérifie le type d'une variable et lève une TypeError si le type ne correspond pas.

    Paramètres:
    variable: La variable à vérifier.
    instance (Type ou tuple[Type]): Le type ou un tuple de types attendus.

    Exception:
    TypeError: Si le type de la variable ne correspond pas au(x) type(s) attendu(s).
    """
    if not isinstance(variable, instance):
        raise TypeError(f"Le paramètre doit être de type {instance}")
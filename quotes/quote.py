import json
import math
from abc import ABC, abstractmethod
from typing import Type


class Quote(ABC):
    """
    Classe parent pour les devises, avec des fonctionnalités pour manipuler les montants
    et appliquer des précisions spécifiques aux classes filles comme Token ou USD.
    """

    # Dictionnaire pour stocker les précisions associées aux classes
    precisions = {
        "Token": 5,
        "USD": 2
    }

    def __init__(self, amount: float):
        """
        Initialise une instance de Quote avec une précision définie par les classes filles
        et applique la troncature de la valeur à cette précision.
        """
        child_class = self.get_child_class()

        # Détermine la précision en fonction de la classe, avec une valeur par défaut de 8 pour Token et 2 pour les autres.
        self.precision = Quote.precisions.get(child_class.__name__, 8 if child_class.__name__ == "Token" else 2)

        # S'assure que la précision utilisée n'est pas supérieure à celle définie dans Quote.precisions (si présente)
        # La ligne originale `discrepancy = Quote.precisions.get(child_class.__name__, self.precision)`
        # et `self.precision = min(self.precision, discrepancy)` est redondante ou incorrecte
        # dans son intention si le but est juste d'appliquer la précision définie pour la classe.
        # J'ai simplifié cela pour que la précision soit directement celle de `precisions` ou la valeur par défaut.

        # Troncature de la valeur à la précision définie
        self.amount = self.truncate_to_precision(amount)

    def get_child_class(self):
        """
        Retourne le type de la classe fille.

        Retourne:
        type: Le type de l'instance courante, qui est le type de la classe fille si héritée.
        """
        return self.__class__

    def truncate_to_precision(self, amount: float) -> float:
        """
        Tronque une valeur à une précision spécifique sans arrondi.

        Paramètres:
        amount (float): Le montant à tronquer.

        Retourne:
        float: Le montant tronqué à la précision définie.
        """
        bot_assert(amount, (float, int))

        factor = 10 ** self.precision
        # Troncature de la valeur
        truncated_amount = math.floor(amount * factor) / factor
        return float(truncated_amount)

    @staticmethod
    def set_precision(class_name: str, precision: int):
        """
        Définit la précision pour une classe donnée.
        :param class_name: Nom de la classe.
        :param precision: Précision à définir.
        """
        Quote.precisions[class_name] = precision

    def __eq__(self, other):
        bot_assert(other, Quote)
        return self.amount == other.amount

    @abstractmethod
    def __str__(self):
        """
        Retourne une représentation en chaîne de caractères du montant.
        """
        pass

    @abstractmethod
    def __lt__(self, other):
        """
        Vérifie si l'instance courante est inférieure à une autre instance ou à un nombre.
        """
        pass

    @abstractmethod
    def __add__(self, other):
        """
        Additionne deux instances.
        """
        pass

    @abstractmethod
    def __radd__(self, other):
        """
        Gère la somme cumulée lorsque l'instance est à droite de l'opérateur.
        """
        pass

    @abstractmethod
    def __sub__(self, other):
        """
        Soustrait une instance d'une autre.
        """
        pass

    @abstractmethod
    def __neg__(self):
        """
        Retourne le montant négatif de l'instance courante.
        """
        pass

    @abstractmethod
    def __mul__(self, other):
        """
        Multiplie l'instance par un nombre ou une autre instance de devise/prix.
        """
        pass

    @abstractmethod
    def __truediv__(self, other):
        """
        Divise l'instance par un nombre, une autre instance de devise, ou un prix.
        """
        pass

    def to_dict(self):
        """Convertit l'objet en dictionnaire."""
        return dict(price=self.amount)

    def to_json(self):
        """Convertit l'objet en JSON."""
        return json.dumps(self.to_dict())


def bot_assert(variable, instance: Type or tuple[Type]):
    if not isinstance(variable, instance):
        raise TypeError(f"Le paramètre doit être de type {instance}")
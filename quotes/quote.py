import ctypes
import json
import math
from abc import abstractmethod
from typing import Type


class Quote(ctypes.Structure):
    """
    Classe parent pour les devises, avec des fonctionnalités pour manipuler les montants
    et appliquer des précisions spécifiques aux classes filles comme $TOKEN ou USD.
    """
    _fields_ = [
        ("amount", ctypes.c_double),
        # Utilisation de c_double pour gérer des montants flottants
        ("precision", ctypes.c_int)
        # Utilisation de c_int pour la précision
    ]

    # Dictionnaire pour stocker les précisions associées aux classes
    precisions = {
        "Token": 5,
        "USD": 2
    }

    def __init__(self, amount):
        """
        Initialise une instance de Quote avec une précision définie par les classes filles
        et applique la troncature de la valeur à cette précision.
        """
        super().__init__()
        child_class = self.get_child_class()

        self.precision = Quote.precisions.get(child_class.__name__, 8 if child_class.__name__ == "Token" else 2)
        discrepancy = Quote.precisions.get(child_class.__name__, self.precision)
        self.precision = min(self.precision, discrepancy)

        # Troncature de la valeur à la précision définie
        self.amount = self.truncate_to_precision(amount)

    def get_child_class(self):
        """
        Retourne le type de la classe fille.

        Retourne:
        type: Le type de l'instance courante, qui est le type de la classe fille si héritée.
        """
        return self.__class__

    def truncate_to_precision(self, amount: float) -> ctypes.c_double:
        """
        Tronque une valeur à une précision spécifique sans arrondi.

        Paramètres:
        amount (float): Le montant à tronquer.

        Retourne:
        ctypes.c_double: Le montant tronqué à la précision définie.
        """
        bot_assert(amount, (float, int))

        factor = 10 ** self.precision
        # Troncature de la valeur et conversion explicite en c_double
        truncated_amount = math.floor(amount * factor) / factor
        return ctypes.c_double(truncated_amount)

    @staticmethod
    def set_precision(class_name, precision):
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
        Retourne une représentation en chaîne de caractères du montant en USDC.

        Retourne:
        str: Le montant de la quote suivi de 'USDC'.
        """
        pass

    @abstractmethod
    def __lt__(self, other):
        """
        Vérifie si l'instance courante est inférieure à une autre instance de USDC ou à un nombre.

        Paramètres:
        other (USDC ou float): L'autre montant à comparer.

        Retourne:
        bool: True si l'instance courante est inférieure, False sinon.

        Exception:
        TypeError: Si other n'est pas un USDC ou un nombre.
        """
        pass

    @abstractmethod
    def __add__(self, other):
        """
        Additionne deux instances de USDC.

        Paramètres:
        other (USDC): L'autre instance de USDC à ajouter.

        Retourne:
        USDC: Une nouvelle instance de USDC représentant la somme.

        Exception:
        TypeError: Si other n'est pas une instance de USDC.
        """
        pass

    @abstractmethod
    def __radd__(self, other):
        """
        Gère la somme cumulée lorsque USDC est à droite de l'opérateur.

        Paramètres:
        other (int, float ou USDC): L'autre opérande.

        Retourne:
        USDC: Une nouvelle instance de USDC représentant la somme.
        """
        pass

    @abstractmethod
    def __sub__(self, other):
        """
        Soustrait une instance de USDC d'une autre.

        Paramètres:
        other (USDC): L'autre instance de USDC à soustraire.

        Retourne:
        USDC: Une nouvelle instance de USDC représentant la différence.

        Exception:
        TypeError: Si other n'est pas une instance de USDC.
        """
        pass

    @abstractmethod
    def __neg__(self):
        """
        Retourne le montant négatif de l'instance courante de USDC.

        Retourne:
        USDC: Une nouvelle instance de USDC représentant le montant négatif.
        """
        pass

    @abstractmethod
    def __mul__(self, other):
        """
        Multiplie l'instance de USDC par un nombre.

        Paramètres:
        other (float): Le nombre à multiplier par le montant en USDC.

        Retourne:
        USDC: Une nouvelle instance de USDC représentant le résultat.

        Exception:
        TypeError: Si other n'est pas un float.
        """
        pass

    @abstractmethod
    def __truediv__(self, other):
        """
        Divise l'instance de USDC par un nombre, une autre instance de USDC, ou un prix.

        Paramètres:
        other (int, float, USDC ou Price): Le diviseur.

        Retourne:
        USDC ou float: Si other est un nombre, retourne une nouvelle instance de USDC.
                       Si other est un USDC ou Price, retourne un float représentant le ratio.

        Exception:
        TypeError: Si other n'est pas un int, float, USDC ou Price.
        ZeroDivisionError: Si une division par zéro est tentée.
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

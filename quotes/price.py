import ctypes
import json

from quotes.quote import bot_assert


class Price(ctypes.Structure):
    """
    Classe Price représentant un prix associé à une devise (quote).

    Fournit des méthodes pour manipuler le prix, effectuer des opérations arithmétiques
    telles que la soustraction, la multiplication, et la division, ainsi que comparer différents prix.
    """
    # Définition des champs pour `ctypes`
    _fields_ = [
        ("price", ctypes.c_double)
        # Utilisation de `c_double` pour représenter le prix
    ]

    # Constante ZERO représentant un prix de 0.0 avec une devise nulle
    ZERO = None

    def __init__(self, price: float, base_symbol, quote_symbol):
        """
        Initialise une instance de Price avec un montant de prix.

        Paramètres:
        price (float): Le montant du prix.

        Exception:
        TypeError: Si le montant du prix n'est pas un float ou un int.
        """
        super().__init__()
        bot_assert(price, float)

        self.price = ctypes.c_double(float(price))
        self.__base = base_symbol
        self.__quote = quote_symbol
        # Utilisation de `c_double` pour le prix

    def get_base(self) -> str:
        """
        Retourne la valeur par défaut actuelle du token.

        :return: Le token par défaut.
        """
        return self.__base

    def get_quote(self) -> str:
        """
        Retourne la valeur par défaut actuelle du token.

        :return: Le token par défaut.
        """
        return self.__quote

    def __str__(self):
        """
        Retourne une représentation en chaîne de caractères du prix.

        Retourne:
        str: Le montant du prix avec la devise (par défaut en USD dans cet exemple).
        """
        return f"{self.price:.2f} {self.__base}/{self.__quote}"

    def __add__(self, other):
        """
        Additionne deux instances de Price.

        Paramètres:
        other (Price): L'autre instance de Price à ajouter.

        Retourne:
        Price: Une nouvelle instance de Price représentant la somme.

        Exception:
        TypeError: Si other n'est pas une instance de Price.
        """
        bot_assert(other, Price)

        return Price(self.price + other.price, self.__base, self.__quote)

    def __sub__(self, other):
        """
        Soustraction de deux prix, en supposant qu'ils aient la même devise.

        Paramètres:
        other (Price): Une autre instance de Price à soustraire.

        Retourne:
        Price: Une nouvelle instance de Price représentant la différence.

        Exception:
        TypeError: Si l'objet other n'est pas de type Price.
        """
        bot_assert(other, Price)

        return Price(self.price - other.price, self.__base, self.__quote)

    def __truediv__(self, other):
        """
        Division d'un prix par un nombre ou un autre Price.

        Paramètres:
        other (float, int, Price): Le diviseur.

        Retourne:
        Price ou float: Si other est un nombre, retourne une nouvelle instance de Price.
                        Si other est une instance de Price, retourne un float représentant le ratio entre les deux prix.

        Exception:
        TypeError: Si l'objet other n'est pas un float, int ou Price.
        ZeroDivisionError: Si la division par zéro est tentée.
        """
        bot_assert(other, (int, float, Price))

        if isinstance(other, (int, float)):
            if other == 0:
                raise ZeroDivisionError("Division par zéro interdite")
            return Price(self.price / other, self.__base, self.__quote)

        if isinstance(other, Price):
            if other.price == 0:
                raise ZeroDivisionError("Division par zéro interdite")
            return self.price / other.price

    def __mul__(self, other):
        """
        Multiplication de Price par un nombre ou une quantité de tokens.

        Paramètres:
        other (float, int, Quantity): Un nombre flottant ou entier pour multiplier le prix,
                                      ou un objet Quantity pour multiplier par un nombre de tokens.

        Retourne:
        Price ou USD: Si other est un nombre, retourne une nouvelle instance de Price.
                       Si other est une instance de Quantity, retourne un montant en USD.

        Exception:
        TypeError: Si l'objet other n'est pas un float, int ou Quantity.
        """
        from quotes.usd import USD
        from quotes.coin import Token

        bot_assert(other, (int, float, Token))

        if isinstance(other, (int, float)):
            return Price(self.price * other, self.__base, self.__quote)

        if isinstance(other, Token):
            amount = self.price * other.amount
            return USD(amount, self.__quote)

    def __eq__(self, other):
        """
        Vérifie si deux instances de Price sont égales.

        Paramètres:
        other (Price): Une autre instance de Price à comparer.

        Retourne:
        bool: True si les montants de prix sont égaux, False sinon.
        """
        bot_assert(other, Price)

        return self.price == other.price

    def __ne__(self, other):
        """
        Vérifie si deux instances de Price ne sont pas égales.

        Paramètres:
        other (Price): Une autre instance de Price à comparer.

        Retourne:
        bool: True si les montants de prix sont différents, False sinon.
        """
        return not self.__eq__(other)

    def __lt__(self, other):
        """
        Vérifie si une instance de Price est inférieure à une autre.

        Paramètres:
        other (Price): Une autre instance de Price à comparer.

        Retourne:
        bool: True si le montant du prix est inférieur, False sinon.
        """
        bot_assert(other, Price)

        return self.price < other.price

    def __le__(self, other):
        """
        Vérifie si une instance de Price est inférieure ou égale à une autre.

        Paramètres:
        other (Price): Une autre instance de Price à comparer.

        Retourne:
        bool: True si le montant du prix est inférieur ou égal, False sinon.
        """
        return self.__lt__(other) or self.__eq__(other)

    def __gt__(self, other):
        """
        Vérifie si une instance de Price est supérieure à une autre.

        Paramètres:
        other (Price): Une autre instance de Price à comparer.

        Retourne:
        bool: True si le montant du prix est supérieur, False sinon.
        """
        bot_assert(other, Price)

        return self.price > other.price

    def __ge__(self, other):
        """
        Vérifie si une instance de Price est supérieure ou égale à une autre.

        Paramètres:
        other (Price): Une autre instance de Price à comparer.

        Retourne:
        bool: True si le montant du prix est supérieur ou égal, False sinon.
        """
        return self.__gt__(other) or self.__eq__(other)

    def to_dict(self):
        """Convertit l'objet en dictionnaire."""
        return dict(price=self.price)

    def to_json(self):
        """Convertit l'objet en JSON."""
        return json.dumps(self.to_dict())

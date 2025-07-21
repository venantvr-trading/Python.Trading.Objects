import json

from quotes.quote import bot_assert


class Price:
    """
    Classe Price représentant un prix associé à une devise (quote).

    Fournit des méthodes pour manipuler le prix, effectuer des opérations arithmétiques
    telles que la soustraction, la multiplication, et la division, ainsi que comparer différents prix.
    """

    # Constante ZERO représentant un prix de 0.0 avec une devise nulle
    ZERO = None

    def __init__(self, price: float, base_symbol: str, quote_symbol: str):
        """
        Initialise une instance de Price avec un montant de prix.

        Paramètres:
        price (float): Le montant du prix.
        base_symbol (str): Le symbole de la devise de base (ex: BTC).
        quote_symbol (str): Le symbole de la devise de cotation (ex: USD).

        Exception:
        TypeError: Si le montant du prix n'est pas un float ou un int.
        """
        bot_assert(price, (float, int))

        self.price = float(price)
        self.__base = base_symbol
        self.__quote = quote_symbol

        if Price.ZERO is None:
            Price.ZERO = Price(0.0, self.__base, self.__quote)

    def get_base(self) -> str:
        """
        Retourne le symbole de la devise de base.

        :return: Le symbole de la devise de base.
        """
        return self.__base

    def get_quote(self) -> str:
        """
        Retourne le symbole de la devise de cotation.

        :return: Le symbole de la devise de cotation.
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
        if isinstance(other, (int, float)):
            if other == 0:
                raise ZeroDivisionError("Division par zéro interdite")
            return Price(self.price / other, self.__base, self.__quote)

        if isinstance(other, Price):
            if other.price == 0:
                raise ZeroDivisionError("Division par zéro interdite")
            return self.price / other.price

        raise TypeError(f"L'opérande doit être un int, float ou Price")

    def __mul__(self, other):
        """
        Multiplication de Price par un nombre ou une quantité de tokens.

        Paramètres:
        other (float, int, Token): Un nombre flottant ou entier pour multiplier le prix,
                                      ou un objet Token pour multiplier par un nombre de tokens.

        Retourne:
        Price ou USD: Si other est un nombre, retourne une nouvelle instance de Price.
                       Si other est une instance de Token, retourne un montant en USD.

        Exception:
        TypeError: Si l'objet other n'est pas un float, int ou Token.
        """
        from quotes.usd import USD
        from quotes.coin import Token

        bot_assert(other, (int, float, Token))

        if isinstance(other, (int, float)):
            return Price(self.price * other, self.__base, self.__quote)

        if isinstance(other, Token):
            amount = self.price * other.amount
            return USD(amount, self.__quote)

        # Should not be reached due to bot_assert, but for explicit return:
        return NotImplemented  # Or raise TypeError as per original design

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
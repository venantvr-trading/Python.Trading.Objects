import json

from quotes.quote import Quote, bot_assert


class USD(Quote):
    """
    Fournit des méthodes pour manipuler et comparer des montants en USD.
    """
    ZERO = None

    def __init__(self, amount: float, quote_symbol: str, _from_factory: bool = False):
        """
        Initialise une instance de USD avec un montant.

        Paramètres:
        amount (float): Le montant en USD.

        Exception:
        TypeError: Si amount n'est pas un float.
        """
        if not _from_factory:
            raise TypeError("Use BotPair.create_token() to instantiate Token.")

        super().__init__(amount, _from_factory)
        bot_assert(amount, (float, int))

        self.__quote = quote_symbol

        if USD.ZERO is None:
            USD.ZERO = USD(0.0, self.__quote)  # Initialise ZERO avec la devise correcte

    def get_quote(self) -> str:
        """
        Retourne la valeur par défaut actuelle du token.

        :return: Le token par défaut.
        """
        return self.__quote

    def __str__(self):
        """
        Retourne une représentation en chaîne de caractères du montant en USD.

        Retourne:
        str: Le montant de la quote suivi de 'USD'.
        """
        return f"{self.amount:.2f} {self.__quote}"

    def __lt__(self, other):
        """
        Vérifie si l'instance courante est inférieure à une autre instance de USD ou à un nombre.

        Paramètres:
        other (USD ou float): L'autre montant à comparer.

        Retourne:
        bool: True si l'instance courante est inférieure, False sinon.

        Exception:
        TypeError: Si other n'est pas un USD ou un nombre.
        """
        if isinstance(other, USD):
            return self.amount < other.amount
        elif isinstance(other, float):
            return self.amount < other
        raise TypeError(f"L'opérande doit être une instance de {self.__quote} ou un nombre (float)")

    def __add__(self, other):
        """
        Additionne deux instances de USD.

        Paramètres:
        other (USD): L'autre instance de USD à ajouter.

        Retourne:
        USD: Une nouvelle instance de USD représentant la somme.

        Exception:
        TypeError: Si other n'est pas une instance de USD.
        """
        bot_assert(other, USD)

        return USD(self.amount + other.amount, self.__quote)

    def __radd__(self, other):
        """
        Gère la somme cumulée lorsque USD est à droite de l'opérateur.

        Paramètres:
        other (int, float ou USD): L'autre opérande.

        Retourne:
        USD: Une nouvelle instance de USD représentant la somme.
        """
        # La méthode __add__ gère déjà l'assertion de type pour 'other'
        # et ne doit pas être appelée directement avec 'other' tel quel s'il n'est pas de type USD.
        # Ici, nous nous attendons à ce que 'other' soit un int ou un float pour __radd__.
        if isinstance(other, (int, float)):
            return USD(self.amount + other, self.__quote)
        return NotImplemented  # Indique que l'opération n'est pas implémentée pour d'autres types

    def __sub__(self, other):
        """
        Soustrait une instance de USD d'une autre.

        Paramètres:
        other (USD): L'autre instance de USD à soustraire.

        Retourne:
        USD: Une nouvelle instance de USD représentant la différence.

        Exception:
        TypeError: Si other n'est pas une instance de USD.
        """
        bot_assert(other, USD)

        return USD(self.amount - other.amount, self.__quote)

    def __neg__(self):
        """
        Retourne le montant négatif de l'instance courante de USD.

        Retourne:
        USD: Une nouvelle instance de USD représentant le montant négatif.
        """
        return USD(-self.amount, self.__quote)

    def __mul__(self, other):
        """
        Multiplie l'instance de USD par un nombre.

        Paramètres:
        other (float): Le nombre à multiplier par le montant en USD.

        Retourne:
        USD: Une nouvelle instance de USD représentant le résultat.

        Exception:
        TypeError: Si other n'est pas un float.
        """
        bot_assert(other, float)

        return USD(self.amount * other, self.__quote)

    def __truediv__(self, other):
        """
        Divise l'instance de USD par un nombre, une autre instance de USD, ou un prix.

        Paramètres:
        other (int, float, USD ou Price): Le diviseur.

        Retourne:
        USD ou float: Si other est un nombre, retourne une nouvelle instance de USD.
                         Si other est un USD ou Price, retourne un float représentant le ratio.

        Exception:
        TypeError: Si other n'est pas un int, float, USD ou Price.
        ZeroDivisionError: Si une division par zéro est tentée.
        """
        from quotes.price import Price
        from quotes.coin import Token

        if isinstance(other, (int, float)):
            if other == 0:
                raise ZeroDivisionError("Division par zéro interdite")
            return USD(self.amount / other, self.__quote)

        if isinstance(other, USD):
            if other.amount == 0:
                raise ZeroDivisionError("Division par zéro interdite")
            return self.amount / other.amount

        if isinstance(other, Price):
            if other.price == 0:
                raise ZeroDivisionError("Division par zéro interdite")
            # Lors de la division d'USD par un Price (ex: USD/BTC), on obtient une quantité de Token (BTC)
            # Nous avons besoin de la base_symbol du Price pour créer le Token résultant.
            return Token(self.amount / other.price, other.get_base())

        raise TypeError(f"L'opérande doit être un int, float, {self.__quote} ou Price")

    def to_dict(self):
        """Convertit l'objet en dictionnaire."""
        return dict(price=self.amount)

    def to_json(self):
        """Convertit l'objet en JSON."""
        return json.dumps(self.to_dict())
import json

from quotes.quote import Quote, bot_assert


class Token(Quote):
    """
    Classe Token représentant une quote spécifique pour la devise $TOKEN.

    Fournit des méthodes pour manipuler et comparer des montants en Bitcoin,
    tout en respectant les types et en assurant la cohérence dans les opérations.
    """

    def __init__(self, amount: float, base_symbol: str):
        """
        Initialise une instance de $TOKEN avec un montant.

        Paramètres:
        amount (float): Le montant de Bitcoin.

        Exception:
        TypeError: Si amount n'est pas un float.
        """
        super().__init__(amount)
        bot_assert(amount, float)

        self.__base = base_symbol

    def get_base(self) -> str:
        """
        Retourne la valeur par défaut actuelle du token.

        :return: Le token par défaut.
        """
        return self.__base

    def __str__(self):
        """
        Retourne une représentation en chaîne de caractères de la quote en Bitcoin.

        Retourne:
        str: Le montant de la quote suivi de '$TOKEN'.
        """
        return f"{self.amount:.8f} {self.__base}"
        # Représentation avec 8 décimales pour Bitcoin

    def __lt__(self, other):
        """
        Vérifie si l'instance courante est inférieure à une autre instance de $TOKEN ou à un nombre.

        Paramètres:
        other ($TOKEN ou float): L'autre montant à comparer.

        Retourne:
        bool: True si l'instance courante est inférieure, False sinon.

        Exception:
        TypeError: Si other n'est pas un $TOKEN ou un nombre.
        """
        if isinstance(other, Token):
            return self.amount < other.amount
        elif isinstance(other, float):
            return self.amount < other
        raise TypeError(f"L'opérande doit être une instance de {self.__base} ou un nombre (float)")

    def __add__(self, other):
        """
        Additionne deux instances de $TOKEN.

        Paramètres:
        other ($TOKEN): L'autre instance de $TOKEN à ajouter.

        Retourne:
        $TOKEN: Une nouvelle instance de $TOKEN représentant la somme.

        Exception:
        TypeError: Si other n'est pas une instance de $TOKEN.
        """
        bot_assert(other, Token)

        return Token(self.amount + other.amount, self.__base)

    def __sub__(self, other):
        """
        Soustrait une instance de $TOKEN d'une autre.

        Paramètres:
        other ($TOKEN): L'autre instance de $TOKEN à soustraire.

        Retourne:
        $TOKEN: Une nouvelle instance de $TOKEN représentant la différence.

        Exception:
        TypeError: Si other n'est pas une instance de $TOKEN.
        """
        bot_assert(other, Token)

        return Token(self.amount - other.amount, self.__base)

    def __neg__(self):
        """
        Retourne le montant négatif de l'instance courante de $TOKEN.

        Retourne:
        $TOKEN: Une nouvelle instance de $TOKEN représentant le montant négatif.
        """
        return Token(-self.amount, self.__base)

    def __mul__(self, other):
        """
        Multiplie l'instance de $TOKEN par un nombre.

        Paramètres:
        other (float): Le nombre à multiplier par le montant en $TOKEN.

        Retourne:
        $TOKEN: Une nouvelle instance de $TOKEN représentant le résultat.

        Exception:
        TypeError: Si other n'est pas un float.
        """
        from quotes.price import Price
        from quotes.usd import USD

        bot_assert(other, (float, Price))

        if isinstance(other, float):
            return Token(self.amount * other, self.__base)

        if isinstance(other, Price):
            return USD(self.amount * other.price, self.__quote)

    def __radd__(self, other):
        pass

    def __truediv__(self, other):
        """
        Divise l'instance de $TOKEN par un nombre ou une autre instance de $TOKEN.

        Paramètres:
        other (int, float ou $TOKEN): Le diviseur.

        Retourne:
        $TOKEN ou float: Si other est un nombre, retourne une nouvelle instance de $TOKEN.
                      Si other est une instance de $TOKEN, retourne un float représentant le ratio.

        Exception:
        TypeError: Si other n'est pas un int, float ou $TOKEN.
        ZeroDivisionError: Si une division par zéro est tentée.
        """
        if isinstance(other, float):
            if other == 0:
                raise ZeroDivisionError("Division par zéro interdite")
            return Token(self.amount / other, self.__base)

        if isinstance(other, Token):
            if other.amount == 0:
                raise ZeroDivisionError("Division par zéro interdite")
            return self.amount / other.amount

        raise TypeError(f"L'opérande doit être un int, float ou {self.__base}")

    def to_dict(self):
        """Convertit l'objet en dictionnaire."""
        return dict(price=self.amount)

    def to_json(self):
        """Convertit l'objet en JSON."""
        return json.dumps(self.to_dict())

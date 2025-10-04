import json
from abc import ABC, abstractmethod
from decimal import Decimal, ROUND_DOWN
from typing import Any, ClassVar, Dict, Union

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_serializer


class Quote(BaseModel, ABC):
    """
    Classe abstraite de base pour toutes les devises.

    Gère les montants et applique une précision spécifique.
    """

    # Configuration Pydantic
    model_config = ConfigDict(
        validate_assignment=True,
        arbitrary_types_allowed=True,
        extra="forbid",
    )

    # Précisions par défaut pour les classes de devise.
    precisions: ClassVar[Dict[str, int]] = {"Token": 5, "USD": 2}

    # Champs Pydantic
    amount: Decimal = Field(..., description="Le montant de la devise")
    precision: int = Field(default=8, description="La précision numérique")

    def __init__(self, amount: Union[Decimal, float, int, str], _from_factory: bool = False, **data):
        """
        Initialise une instance de Quote.

        Paramètres:
        amount (float): Le montant de la devise.
        _from_factory (bool): Interne, indique si l'instance est créée via une factory.
        """
        # La vérification _from_factory est effectuée dans les classes concrètes héritant de Quote.

        # Convertir en Decimal si nécessaire
        if not isinstance(amount, Decimal):
            amount = Decimal(str(amount))

        # Si precision n'est pas dans data, on la calcule
        if "precision" not in data:
            child_class = self.__class__
            # Détermine la précision en fonction du nom de la classe fille.
            precision = Quote.precisions.get(
                child_class.__name__, 8 if child_class.__name__ == "Token" else 2
            )
            # Tronque le montant seulement si on calcule la précision nous-mêmes
            truncated_amount = self._truncate_to_precision_static(amount, precision)
        else:
            precision = data.pop("precision")  # Retirer de data pour éviter les doublons
            # Ne pas retronquer - le montant a déjà été tronqué par la classe fille
            truncated_amount = amount

        # Appelle le constructeur de BaseModel
        super().__init__(amount=truncated_amount, precision=precision, **data)

    @field_validator("amount", mode="before")
    @classmethod
    def validate_amount(cls, v):
        """Valide que le montant est un nombre et le convertit en Decimal."""
        if isinstance(v, Decimal):
            return v
        if isinstance(v, (float, int, str)):
            return Decimal(str(v))
        raise TypeError(f"Amount must be Decimal, float, int or str, got {type(v)}")

    @model_serializer
    def serialize_model(self) -> Dict[str, Any]:
        """Sérialise le modèle avec les float en string pour préserver la précision."""
        return {
            "amount": str(self.amount),
            "precision": self.precision,
        }

    @staticmethod
    def _truncate_to_precision_static(amount: Union[Decimal, float, int], precision: int) -> Decimal:
        """
        Tronque une valeur à la précision définie (sans arrondi) en utilisant Decimal.

        Paramètres:
        amount (Decimal|float|int): Le montant à tronquer.
        precision (int): La précision à appliquer.

        Retourne:
        Decimal: Le montant tronqué.
        """
        if not isinstance(amount, Decimal):
            amount = Decimal(str(amount))

        # Créer le quantizer basé sur la précision (ex: 0.01 pour precision=2)
        quantizer = Decimal(10) ** -precision
        # Tronquer vers le bas (ROUND_DOWN)
        return amount.quantize(quantizer, rounding=ROUND_DOWN)

    def truncate_to_precision(self, amount: Union[Decimal, float, int]) -> Decimal:
        """
        Tronque une valeur à la précision définie (sans arrondi).

        Paramètres:
        amount (Decimal|float|int): Le montant à tronquer.

        Retourne:
        Decimal: Le montant tronqué.
        """
        return self._truncate_to_precision_static(amount, self.precision)

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
        from python_trading_objects.quotes.assertion import bot_assert

        bot_assert(other, Quote)
        return self.amount == other.amount

    def __hash__(self):
        """Rend la classe hashable pour utilisation dans des sets/dicts."""
        return hash((self.__class__.__name__, self.amount))

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
        """Convertit l'objet en dictionnaire avec les float en string pour préserver la précision."""
        return {"price": str(self.amount)}

    def to_json(self):
        """Convertit l'objet en JSON."""
        return json.dumps(self.to_dict())

    def is_positive(self) -> bool:
        """
        Vérifie si le montant de la devise est strictement positif.

        Retourne:
        bool: True si le montant est > 0, False sinon.
        """
        return self.amount > 0

    def is_zero(self) -> bool:
        """
        Vérifie si le montant de la devise est égal à zéro.

        Retourne:
        bool: True si le montant est == 0, False sinon.
        """
        return self.amount == 0

    def is_negative(self) -> bool:
        """
        Vérifie si le montant de la devise est strictement négatif.

        Retourne:
        bool: True si le montant est < 0, False sinon.
        """
        return self.amount < 0

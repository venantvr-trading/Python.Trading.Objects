from typing import Type


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

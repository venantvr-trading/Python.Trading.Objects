# Python.Trading.Objects

## Description

`Python.Trading.Objects` est une bibliothèque Python pour la gestion d'objets de trading, incluant des représentations de montants (tokens, USD), de prix et une fabrique
pour créer ces objets en fonction d'une paire de devises.

## Installation

Cette bibliothèque est conçue pour être installée en tant que package Python.

```bash
pip install .
```

ou, si vous souhaitez l'installer en mode "editable" pour le développement :

```bash
pip install -e .
```

### Prérequis

* Python \>= 3.8

## Utilisation

### Création d'objets avec la fabrique `BotPair`

La classe `BotPair` agit comme une fabrique pour garantir la cohérence des types et des symboles de devises.

```python
from venantvr.quotes import BotPair

# Crée une fabrique pour la paire Bitcoin/US Dollar
bot_pair = BotPair("BTC/USD")

# Crée un Token pour la devise de base (BTC)
btc_amount = bot_pair.create_token(1.5)
print(f"Token créé: {btc_amount}")  # Affiche "1.50000000 BTC"

# Crée un Price pour la paire
btc_price = bot_pair.create_price(25000.0)
print(f"Prix créé: {btc_price}")  # Affiche "25000.00 BTC/USD"

# Crée un objet USD pour la devise de cotation
usd_amount = bot_pair.create_usd(100.0)
print(f"Montant USD créé: {usd_amount}")  # Affiche "100.00 USD"
```

### Opérations arithmétiques

Les objets de la bibliothèque surchargent les opérateurs pour permettre des calculs intuitifs.

#### `Token`

```python
token1 = bot_pair.create_token(5.0)
token2 = bot_pair.create_token(3.0)

# Addition
result_add = token1 + token2
print(f"Addition: {result_add}")  # Affiche "8.00000000 BTC"

# Soustraction
result_sub = token1 - token2
print(f"Soustraction: {result_sub}")  # Affiche "2.00000000 BTC"

# Multiplication par un float
result_mul_float = token1 * 2.5
print(f"Multiplication par un float: {result_mul_float}")  # Affiche "12.50000000 BTC"

# Division par un float
result_div_float = token1 / 2.0
print(f"Division par un float: {result_div_float}")  # Affiche "2.50000000 BTC"
```

#### `USD`

```python
usd1 = bot_pair.create_usd(50.0)
usd2 = bot_pair.create_usd(30.0)

# Addition
result_add = usd1 + usd2
print(f"Addition: {result_add}")  # Affiche "80.00 USD"

# Multiplication par un float
result_mul_float = usd1 * 2.5
print(f"Multiplication par un float: {result_mul_float}")  # Affiche "125.00 USD"

# Division par un Price pour obtenir un Token
price = bot_pair.create_price(20000.0)
result_div_price = usd1 / price
print(f"Division par un Price: {result_div_price}")  # Affiche "0.00250000 BTC"
```

#### `Price`

```python
price = bot_pair.create_price(20000.0)
token = bot_pair.create_token(0.5)

# Multiplication d'un Price par un Token
result = price * token
print(f"Prix * Token: {result}")  # Affiche "10000.00 USD"
```

### Classes principales

* **`Quote`**: Classe de base abstraite pour les devises, gérant la précision des montants.
* **`BotPair`**: Fabrique de classes pour créer des instances de `Token`, `Price` et `USD` de manière sécurisée pour une paire de devises donnée.
* **`Token`**: Représente un montant de la devise de base (par exemple, 1.5 BTC).
* **`USD`**: Représente un montant de la devise de cotation (par exemple, 100 USD). Le nom est un peu générique, car il peut représenter n'importe quelle devise de
  cotation (JPY, EUR, etc.).
* **`Price`**: Représente le prix d'une devise de base par rapport à une devise de cotation (par exemple, 25000 BTC/USD).

## Tests

La bibliothèque utilise `pytest` pour ses tests unitaires. Les tests couvrent la création d'objets, les opérations arithmétiques, les comparaisons et la gestion des
erreurs (comme l'instanciation directe des classes ou la division par zéro).

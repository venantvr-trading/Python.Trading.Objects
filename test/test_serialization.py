"""
Tests de sérialisation et désérialisation avec Decimal pour préserver la précision.
"""

import json
from dataclasses import asdict, is_dataclass
from decimal import Decimal

from pydantic import BaseModel

from python_trading_objects.quotes import BotPair, Token
from python_trading_objects.quotes.swap import (
    SwapQuote,
    SwapRequest,
)


class TestDecimalSerialization:
    """Tests de sérialisation avec Decimal pour garantir la précision."""

    def test_token_uses_decimal(self):
        """Vérifie que Token utilise Decimal pour le montant."""
        pair = BotPair("BTC/USD")
        token = pair.create_token(1.23456789012345678)

        # Vérifie que l'amount est un Decimal
        assert isinstance(token.amount, Decimal)
        assert token.amount == Decimal("1.23456")  # Tronqué à la précision

    def test_token_serialization_to_string(self):
        """Vérifie que la sérialisation Pydantic convertit Decimal en string."""
        pair = BotPair("BTC/USD")
        token = pair.create_token(1.23456789012345678)

        # Test model_dump()
        data = token.model_dump()
        assert isinstance(data["amount"], str)
        assert data["amount"] == "1.23456"

        # Test to_dict()
        dict_data = token.to_dict()
        assert isinstance(dict_data["price"], str)
        assert dict_data["price"] == "1.23456"

    def test_token_json_serialization(self):
        """Vérifie que la sérialisation JSON préserve la précision."""
        pair = BotPair("BTC/USD")
        token = pair.create_token(1.23456789012345678)

        # Sérialise en JSON
        json_str = json.dumps(token.model_dump())
        assert '"amount": "1.23456"' in json_str

        # Désérialise
        data = json.loads(json_str)
        assert data["amount"] == "1.23456"

        # Reconstruit le Decimal
        amount_decimal = Decimal(data["amount"])
        assert amount_decimal == token.amount

    def test_precision_preservation_with_very_precise_numbers(self):
        """Vérifie qu'aucune précision n'est perdue avec des nombres très précis."""
        pair = BotPair("ETH/USD")

        # Nombre avec beaucoup de décimales
        original = 0.123456789012345
        token = pair.create_token(original)

        # Le montant est tronqué selon la précision (5 pour Token)
        expected = Decimal("0.12345")
        assert token.amount == expected

        # Sérialise
        data = token.model_dump()
        assert data["amount"] == "0.12345"

        # Vérifie qu'on peut reconstruire exactement
        reconstructed = Decimal(data["amount"])
        assert reconstructed == expected

    def test_arithmetic_operations_preserve_decimal(self):
        """Vérifie que les opérations arithmétiques préservent le type Decimal."""
        pair = BotPair("BTC/USD")
        token1 = pair.create_token(1.5)
        token2 = pair.create_token(2.3)

        # Addition
        result = token1 + token2
        assert isinstance(result.amount, Decimal)

        # Soustraction
        result = token2 - token1
        assert isinstance(result.amount, Decimal)

        # Multiplication
        result = token1 * 2
        assert isinstance(result.amount, Decimal)

        # Division
        result = token1 / 2
        assert isinstance(result.amount, Decimal)

    def test_comparison_with_decimal(self):
        """Vérifie que les comparaisons fonctionnent avec Decimal."""
        pair = BotPair("BTC/USD")
        token1 = pair.create_token(1.5)
        token2 = pair.create_token(2.5)

        assert token1 < token2
        assert token2 > token1
        assert token1 == token1

        # Comparaison avec un nombre
        assert token1 < 2.0


class TestPreparePayloadCompatibility:
    """Tests de compatibilité avec la méthode _prepare_payload."""

    def _prepare_payload(self, payload, event_name: str):
        """
        Simule la méthode _prepare_payload de votre système.
        """
        message = None
        schema_to_register = None

        if is_dataclass(payload):
            schema_to_register = type(payload)
            message = asdict(payload)
        elif isinstance(payload, BaseModel):
            schema_to_register = type(payload)
            message = payload.model_dump()
        elif isinstance(payload, dict):
            message = payload
        else:
            raise ValueError(f"Type de payload non supporté : {type(payload)}")

        return message, schema_to_register

    def test_token_with_prepare_payload(self):
        """Vérifie que Token fonctionne avec _prepare_payload."""
        pair = BotPair("BTC/USD")
        token = pair.create_token(1.23456789)

        # Prépare le payload
        message, schema = self._prepare_payload(token, "token_created")

        # Vérifie que c'est un dict
        assert isinstance(message, dict)
        assert schema == Token

        # Vérifie que les montants sont des strings
        assert isinstance(message["amount"], str)
        assert message["amount"] == "1.23456"

    def test_swap_request_with_prepare_payload(self):
        """Vérifie que SwapRequest fonctionne avec _prepare_payload."""
        swap = SwapRequest("BTC", "USDC", 1.5)

        # Prépare le payload
        message, schema = self._prepare_payload(swap, "swap_requested")

        # Vérifie que c'est un dict
        assert isinstance(message, dict)
        assert schema == SwapRequest

        # Vérifie que le montant est une string
        assert isinstance(message["amount"], str)
        assert message["amount"] == "1.5"

    def test_swap_quote_with_prepare_payload(self):
        """Vérifie que SwapQuote fonctionne avec _prepare_payload."""
        quote = SwapQuote(25000.0, "BTC", "USDC", 0.001, 0.01)

        # Prépare le payload
        message, schema = self._prepare_payload(quote, "swap_quoted")

        # Vérifie que c'est un dict
        assert isinstance(message, dict)
        assert schema == SwapQuote

        # Vérifie que tous les float sont des strings
        assert isinstance(message["rate"], str)
        assert isinstance(message["fees"], str)
        assert isinstance(message["slippage"], str)

    def test_json_roundtrip_preserves_precision(self):
        """Vérifie qu'un round-trip JSON préserve la précision."""
        pair = BotPair("BTC/USD")
        token = pair.create_token(1.23456789)

        # Sérialise
        message, _ = self._prepare_payload(token, "test")
        json_str = json.dumps(message)

        # Désérialise
        data = json.loads(json_str)

        # Vérifie que la précision est préservée
        assert data["amount"] == "1.23456"

        # Reconstruit
        reconstructed = Decimal(data["amount"])
        assert reconstructed == token.amount


class TestEdgeCases:
    """Tests de cas limites avec Decimal."""

    def test_very_small_numbers(self):
        """Vérifie le comportement avec de très petits nombres."""
        pair = BotPair("BTC/USD")
        token = pair.create_token(0.00000001)  # 1 satoshi

        assert isinstance(token.amount, Decimal)
        data = token.model_dump()
        assert data["amount"] == "0.00000"  # Tronqué à la précision 5

    def test_very_large_numbers(self):
        """Vérifie le comportement avec de très grands nombres."""
        pair = BotPair("BTC/USD")
        token = pair.create_token(999999999.123456)

        assert isinstance(token.amount, Decimal)
        data = token.model_dump()
        assert data["amount"] == "999999999.12345"

    def test_zero_value(self):
        """Vérifie le comportement avec zéro."""
        pair = BotPair("BTC/USD")
        token = pair.create_token(0.0)

        assert isinstance(token.amount, Decimal)
        assert token.amount == Decimal("0")
        data = token.model_dump()
        # Le format peut inclure les zéros selon la précision
        assert data["amount"] in ("0", "0.00000")

    def test_negative_values(self):
        """Vérifie le comportement avec des valeurs négatives."""
        pair = BotPair("BTC/USD")
        token = pair.create_token(10.5)
        neg_token = -token

        assert isinstance(neg_token.amount, Decimal)
        assert neg_token.amount < 0
        data = neg_token.model_dump()
        # Le format peut inclure des zéros selon la précision
        assert data["amount"].startswith("-10.5")

    def test_precision_truncation(self):
        """Vérifie que la troncature fonctionne correctement avec Decimal."""
        pair = BotPair("BTC/USD")

        # Token a une précision de 5
        token = pair.create_token(1.999999)
        # Devrait être tronqué à 1.99999 (pas arrondi)
        assert token.amount == Decimal("1.99999")

        # USD a une précision de 2
        usd = pair.create_usd(2.999)
        # Devrait être tronqué à 2.99 (pas arrondi)
        assert usd.amount == Decimal("2.99")


class TestDeserialization:
    """Tests de désérialisation depuis JSON."""

    def test_deserialize_from_json_string(self):
        """Vérifie qu'on peut désérialiser depuis JSON avec des strings."""
        json_data = {
            "amount": "1.23456",
            "precision": 5,
            "base_symbol": "BTC",
        }

        # Pydantic devrait pouvoir reconstruire depuis ce dict
        # (nécessite que la classe accepte les strings)
        from python_trading_objects.quotes.quote import Quote

        # Le validator devrait convertir la string en Decimal
        amount = Quote.validate_amount("1.23456")
        assert isinstance(amount, Decimal)
        assert amount == Decimal("1.23456")

    def test_deserialize_preserves_exact_value(self):
        """Vérifie qu'aucune perte de précision lors de la désérialisation."""
        original_value = "0.123456789012345"

        # Convertit en Decimal
        decimal_value = Decimal(original_value)

        # Sérialise en string
        serialized = str(decimal_value)

        # Désérialise
        deserialized = Decimal(serialized)

        # Vérifie l'égalité parfaite
        assert deserialized == decimal_value

    def test_float_vs_decimal_precision(self):
        """Démontre la différence entre float et Decimal."""
        value = 0.1 + 0.2

        # Avec float (perte de précision)
        float_result = value
        assert float_result != 0.3  # Float precision issue!

        # Avec Decimal (précision exacte)
        decimal_result = Decimal("0.1") + Decimal("0.2")
        assert decimal_result == Decimal("0.3")  # Perfect!

        # Après sérialisation JSON
        float_json = json.dumps({"value": float_result})
        decimal_json = json.dumps({"value": str(decimal_result)})

        assert "0.30000000000000004" in float_json  # Float precision loss
        assert '"0.3"' in decimal_json  # Decimal preserves precision

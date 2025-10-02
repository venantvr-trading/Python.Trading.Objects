"""
Legacy USD class for backward compatibility.
New code should use Asset class instead.
"""
from venantvr.quotes.asset import USD

# Re-export USD from asset module for backward compatibility
__all__ = ['USD']

# Optional: Show deprecation warning when this module is imported
# import warnings
# warnings.warn(
#     "venantvr.quotes.usd is deprecated. Use venantvr.quotes.asset instead.",
#     DeprecationWarning,
#     stacklevel=2
# )

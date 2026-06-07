"""Number utilities for numeric operations."""


class NumberUtils:
    """Utility class for numeric operations."""

    @staticmethod
    def format_currency(value: float, decimals: int = 2) -> float:
        """Format currency value with specified decimal places.

        Args:
            value: The currency value to format.
            decimals: Number of decimal places (default: 2).

        Returns:
            Rounded currency value.
        """
        return round(value, decimals)

    @staticmethod
    def ensure_non_negative(value: float) -> float:
        """Ensure value is not negative.

        Args:
            value: The value to check.

        Returns:
            max(0, value) to prevent negative values.
        """
        return max(0, value)

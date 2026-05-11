class StockException(Exception):
    """Base exception for stock operations."""


class InsufficientStockError(StockException):
    """Raised when stock quantity is insufficient."""


class StockNotFoundError(StockException):
    """Raised when stock record is not found."""


class InvalidQuantityError(StockException):
    """Raised when provided quantity values are invalid."""

class MarketLabException(Exception):
    """Base exception for MarketLab AI"""
    def __init__(self, message: str, details: dict = None):
        super().__init__(message)
        self.message = message
        self.details = details or {}


class InstrumentNotFoundError(MarketLabException):
    pass


class AmbiguousInstrumentError(MarketLabException):
    pass


class MarketDataValidationError(MarketLabException):
    pass


class InsufficientEvidenceError(MarketLabException):
    pass


class BacktestExecutionError(MarketLabException):
    pass


class LookAheadBiasDetectedError(MarketLabException):
    pass

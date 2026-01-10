
class LectorcitoError(Exception):
    """Error base de la aplicación."""


class ConfigError(LectorcitoError):
    """Error relacionado con configuración."""


class ProcessingCancelled(LectorcitoError):
    """El usuario canceló un procesamiento."""

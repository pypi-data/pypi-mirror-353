
from .authorization.authorization import OpenFgaConfig
from .authorization.authorization import OpenFgaService
from .authorization.authorization import OpenFgaServiceSingleton


__all__ = [
    "OpenFgaConfig",
    "OpenFgaService",
    "OpenFgaServiceSingleton"
]

__import__('pkg_resources').declare_namespace(__name__)

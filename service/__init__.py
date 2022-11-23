"""Export all Namespaces and named with modules' name

"""
from .aiida.api import ns as aiida
from .hello.api import ns as hello
from .system.api import ns as system

__all__ = (aiida, hello, system)

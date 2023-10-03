import sys
from importlib.metadata import version as get_version

version = get_version("earhorn")
__version__ = version

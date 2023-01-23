import sys

if sys.version_info < (3, 8):
    from importlib_metadata import version as get_version
else:
    from importlib.metadata import version as get_version

version = get_version("earhorn")
__version__ = version

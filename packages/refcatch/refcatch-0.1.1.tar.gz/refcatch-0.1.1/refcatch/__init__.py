"""
RefCatch - A package for processing academic references from plaintext files.

This package extracts references from plaintext files (markdown, txt, etc.),
attempts to find their DOIs, and outputs the results.
"""

from .core import refcatch

try:
    from ._version import version as __version__
except ModuleNotFoundError:
    __version__ = "dev"  # Fallback for development mode

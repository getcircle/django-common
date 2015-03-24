"""
The `compat` module provides compatibility wrappers around optional packages.
"""

try:
    from service import metrics
except ImportError:
    metrics = None

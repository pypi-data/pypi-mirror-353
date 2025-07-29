"""
Main entry point for the ADRI module.

Allows running the package as: python -m adri
"""

import sys
from .cli import main

if __name__ == "__main__":
    sys.exit(main())

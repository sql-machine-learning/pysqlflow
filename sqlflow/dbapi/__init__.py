"""SQLFlow implementation of the Database API Specification v2.0

   Python Database API Specification v2.0 (DB-API):
   https://www.python.org/dev/peps/pep-0249/
"""

apilevel = "2.0"

# Threads may share the module, but not connections.
threadsafety = 2

__all__ = [
    "apilevel",
    "threadsafety",
]


"""
limiter.py — Shared slowapi Limiter instance.

Defined here (not in main.py) so that route modules (auth.py etc.)
can import it without creating a circular dependency on main.py.
main.py imports this object and attaches it to app.state.
"""

from slowapi import Limiter
from slowapi.util import get_remote_address

limiter = Limiter(key_func=get_remote_address, default_limits=["200/minute"])

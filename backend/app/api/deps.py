"""Shared API dependencies.

`current_user` now validates a JWT Bearer token and returns the user id (string)
used as `user_id` across the app's tables. See app/auth.py.
"""
from __future__ import annotations

from app.auth import get_current_user

current_user = get_current_user

"""
CRUD операции для всех моделей
"""

from .user import user_crud
from .mood_entry import mood_entry_crud

__all__ = ["user_crud", "mood_entry_crud"]
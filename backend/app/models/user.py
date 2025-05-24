"""
User model.
"""

from pydantic import BaseModel


class User(BaseModel):
    id: str
    email: str
    name: str
    role: str

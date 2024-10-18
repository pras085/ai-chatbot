from typing import Any
from pydantic import BaseModel

class JwtUser(BaseModel):
    username: str = None
    id: int = None
    role: str = 'user'
    exp: int = None

    def __init__(self, username: str, id: int, role: str, exp: int = 0, **kw: Any):
        super().__init__(**kw)
        self.username = username
        self.id = id
        self.role = role
        self.exp = exp
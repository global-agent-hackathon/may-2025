from pydantic import BaseModel


class User(BaseModel):
    user_id: str

    @property
    def is_authenticated(self) -> bool:
        return True

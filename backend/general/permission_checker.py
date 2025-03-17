from fastapi import status, Depends, HTTPException

from models.user import Role, UserRead
from general.auth import get_current_active_user

class PermissionChecker:
    def __init__(self, roles: list[Role]) -> None:
        self.roles = roles

    def __call__(self, user: UserRead = Depends(get_current_active_user)) -> bool:
        if user.role not in self.roles:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN)
        return True

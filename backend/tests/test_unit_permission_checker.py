import pytest
from unittest.mock import Mock
from fastapi import HTTPException
from general.permission_checker import PermissionChecker
from models.user import Role

# Модуль проверки ролей
class TestPermissionChecker:    
    def test_permission_checker_allowed_role(self):
        """Тест 1: Проверить доступ пользователя с разрешённой ролью."""
        permission_checker = PermissionChecker(roles=[Role.ADMIN, Role.MANAGER])
        mock_user = Mock()
        mock_user.role = Role.ADMIN
        
        result = permission_checker.__call__(mock_user)
        
        assert result is True

    def test_permission_checker_denied_role(self):
        """Тест 2: Проверить запрет доступа пользователю с неправильной ролью."""
        permission_checker = PermissionChecker(roles=[Role.ADMIN, Role.MANAGER])
        mock_user = Mock()
        mock_user.role = Role.USER
        
        with pytest.raises(HTTPException) as exc_info:
            permission_checker.__call__(mock_user)
        
        assert exc_info.value.status_code == 403
        assert "Доступ запрещён" in str(exc_info.value.detail)

    def test_permission_checker_single_role(self):
        """Тест 3: Проверить работу с одной разрешённой ролью."""
        permission_checker = PermissionChecker(roles=[Role.MANAGER])
        mock_user = Mock()
        mock_user.role = Role.MANAGER
        
        result = permission_checker.__call__(mock_user)
        
        assert result is True

    def test_permission_checker_empty_roles(self):
        """Тест 4: Проверить работу с пустым списком ролей."""
        permission_checker = PermissionChecker(roles=[])
        mock_user = Mock()
        mock_user.role = Role.ADMIN
        
        with pytest.raises(HTTPException) as exc_info:
            permission_checker.__call__(mock_user)
        
        assert exc_info.value.status_code == 403

    def test_permission_checker_no_role(self):
        """Тест 5: Проверить обработку пользователя без роли."""
        permission_checker = PermissionChecker(roles=[Role.ADMIN])
        mock_user = Mock()
        mock_user.role = None
        
        with pytest.raises(HTTPException) as exc_info:
            permission_checker.__call__(mock_user)
        
        assert exc_info.value.status_code == 403

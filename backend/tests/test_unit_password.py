from unittest.mock import patch
from general.password import get_password_hash, verify_password


# Модуль работы с паролями
class TestPassword:
    def test_get_password_hash_success(self):
        """Тест 1: Проверить вызов функции генерации хэша пароля."""
        test_password = "надежныйпароль123"
        
        with patch('general.password.pwd_context') as mock_pwd:
            mock_pwd.hash.return_value = "хэшированный_пароль"
            
            result = get_password_hash(test_password)
            
            assert result == "хэшированный_пароль"
            mock_pwd.hash.assert_called_once_with(test_password)


    def test_get_password_hash_empty(self):
        """Тест 2: Проверить обработку пустого пароля."""
        with patch('general.password.pwd_context') as mock_pwd:
            mock_pwd.hash.return_value = "хэш_пустого_пароля"
            
            result = get_password_hash("")
            
            assert result == "хэш_пустого_пароля"
            mock_pwd.hash.assert_called_once_with("")

    def test_verify_password_success(self):
        """Тест 3: Проверить верификацию правильного пароля"""
        plain_password = "пароль123"
        password_hash = "правильный_хэш"
        
        with patch('general.password.pwd_context') as mock_pwd:
            mock_pwd.verify.return_value = True
            
            result = verify_password(plain_password, password_hash)
            
            assert result is True
            mock_pwd.verify.assert_called_once_with(plain_password, password_hash)

    def test_verify_password_wrong(self):
        """Тест 4: Проверить верификацию неправильного пароля"""
        plain_password = "неправильныйпароль"
        password_hash = "правильный_хэш"
        
        with patch('general.password.pwd_context') as mock_pwd:
            mock_pwd.verify.return_value = False
            
            result = verify_password(plain_password, password_hash)
            
            assert result is False
            mock_pwd.verify.assert_called_once_with(plain_password, password_hash)

import pytest
from fastapi.testclient import TestClient
from datetime import datetime, timedelta
import jwt

from main import app
from models.user import User
from general.auth import (
    Role, 
    create_access_token, 
    SECRET_KEY, 
    ALGORITHM
)
from general.password import get_password_hash
from general.user import read_user_by_username

from sqlmodel import SQLModel, create_engine, Session
from sqlmodel.pool import StaticPool

# Тестовая БД
DATABASE_URL = "sqlite:///:memory:"

engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)

# Тестирование интеграции модуля аутентификации и базы данных
class TestAuthIntegration:
    
    @pytest.fixture(autouse=True)
    def setup_db(self):
        """Фикстура для подготовки и очистки БД перед каждым тестом"""
        SQLModel.metadata.create_all(engine)
        self.session = Session(engine)
        
        # Подменяем зависимость БД
        from api.deps import get_session
        def override_get_session():
            try:
                yield self.session
            finally:
                pass
        
        app.dependency_overrides[get_session] = override_get_session
        
        self.client = TestClient(app)
        yield
        
        # Очистка после теста
        app.dependency_overrides.clear()
        self.session.close()
        SQLModel.metadata.drop_all(engine)
    
    def create_test_user(self, username, password, role=Role.USER):
        """Создать тестового пользователя в БД"""
        user = User(
            username=username,
            password_hash=get_password_hash(password),
            role=role,
            created_at=datetime.utcnow()
        )
        self.session.add(user)
        self.session.commit()
        self.session.refresh(user)
        return user
    
    def decode_token(self, token):
        """Декодировать JWT токен"""
        return jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
    
    # Тесты для функции login_for_access_token
    
    def test_login_success_valid_credentials(self):
        """Тест 1: Проверить успешную аутентификацию пользователя с валидными учетными данными"""
        self.create_test_user('test_user', 'valid_password')
        
        form_data = {
            "username": "test_user",
            "password": "valid_password"
        }
        
        response = self.client.post("/login/", data=form_data)
        
        assert response.status_code == 200
        
        cookies = response.cookies
        assert "access_token" in cookies
        assert "role" in cookies
        assert cookies["role"] == Role.USER.value
        
        access_token = cookies["access_token"]
        payload = self.decode_token(access_token)
        assert payload["sub"] == "test_user"
        assert payload["role"] == Role.USER.value
        
        user_data = response.json()
        assert user_data["username"] == "test_user"
        assert user_data["role"] == Role.USER.value
        
        user_in_db = read_user_by_username("test_user", self.session)
        assert user_in_db is not None
        assert user_in_db.username == "test_user"
    
    def test_login_invalid_username(self):
        """Тест 2: Проверить обработку неверного логина"""
        form_data = {
            "username": "non_existent_user",
            "password": "any_password"
        }
        
        response = self.client.post("/login/", data=form_data)
        
        assert response.status_code == 401
        assert response.json()["detail"] == "Некорректный логин или пароль"
        
        cookies = response.cookies
        if hasattr(cookies, 'get'):
            assert cookies.get("access_token") in [None, ""]
            assert cookies.get("role") in [None, ""]
    
    def test_login_invalid_password(self):
        """Тест 3: Проверить обработку неверного пароля"""
        self.create_test_user('test_user', 'correct_password')
        
        form_data = {
            "username": "test_user",
            "password": "wrong_password"
        }
        
        response = self.client.post("/login/", data=form_data)
        
        assert response.status_code == 401
        assert response.json()["detail"] == "Некорректный логин или пароль"
        
        cookies = response.cookies
        if hasattr(cookies, 'get'):
            assert cookies.get("access_token") in [None, ""]
            assert cookies.get("role") in [None, ""]
    
    # Тесты для функции logout
    
    def test_logout_success(self):
        """Тест 4: Проверить корректный выход из системы"""
        self.create_test_user('logout_user', 'password123')
        
        login_response = self.client.post("/login/", data={
            "username": "logout_user",
            "password": "password123"
        })
        
        access_token = login_response.cookies.get("access_token")
        role_cookie = login_response.cookies.get("role")
        
        self.client.cookies.set("access_token", access_token)
        self.client.cookies.set("role", role_cookie)
        
        response = self.client.post("/login/logout/")
        
        assert response.status_code == 200
        assert response.json() == {"ok": True}
        
        user_in_db = read_user_by_username("logout_user", self.session)
        assert user_in_db is not None
    
    # Тесты для функции read_users_me
    
    def test_read_users_me_valid_token(self):
        """Тест 5: Проверить получение данных текущего пользователя с валидным токеном"""
        test_user = self.create_test_user('me_user', 'password123', Role.USER)
        
        access_token = create_access_token(test_user, timedelta(minutes=30))
        
        self.client.cookies.set("access_token", access_token)
        self.client.cookies.set("role", Role.USER.value)
        
        response = self.client.get("/login/me/")
        
        assert response.status_code == 200
        
        user_data = response.json()
        assert user_data["username"] == "me_user"
        assert user_data["role"] == Role.USER.value
    
    def test_read_users_me_user_deleted_after_token(self):
        """Тест 6: Проверить обработку случая, когда пользователь удален из БД после выпуска токена"""
        test_user = self.create_test_user('deleted_user', 'password123', Role.USER)
        
        access_token = create_access_token(test_user, timedelta(minutes=30))
        
        self.session.delete(test_user)
        self.session.commit()
        
        self.client.cookies.set("access_token", access_token)
        self.client.cookies.set("role", Role.USER.value)
        
        response = self.client.get("/login/me/")
        
        assert response.status_code == 401
        assert "Недействительные учетные данные" in response.json()["detail"]
        
        response2 = self.client.get("/login/me/")
        assert response2.status_code == 401
    
    def test_read_users_me_role_changed(self):
        """Тест 7: Проверить обработку изменения роли пользователя в БД"""
        test_user = self.create_test_user('role_changed_user', 'password123', Role.USER)
        
        access_token = create_access_token(test_user, timedelta(minutes=30))
        
        test_user.role = Role.ADMIN
        self.session.add(test_user)
        self.session.commit()
        self.session.refresh(test_user)
        
        self.client.cookies.set("access_token", access_token)
        self.client.cookies.set("role", Role.USER.value)
        
        response = self.client.get("/login/me/")
        
        assert response.status_code == 401
        assert "Недействительные учетные данные" in response.json()["detail"]
        
        response2 = self.client.get("/login/me/")
        assert response2.status_code == 401

import pytest
from fastapi.testclient import TestClient
from datetime import timedelta
from unittest.mock import AsyncMock, patch

from main import app
from models.user import User
from models.item import Item
from models.brand import Brand
from models.category import Category
from general.auth import Role, create_access_token
from general.password import get_password_hash

from sqlmodel import SQLModel, create_engine, Session
from sqlmodel.pool import StaticPool

DATABASE_URL = "sqlite:///:memory:"

engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)

class TestBuyItemIntegration:
    
    @pytest.fixture(autouse=True)
    def setup_db(self):
        SQLModel.metadata.create_all(engine)
        self.session = Session(engine)
        
        from api.deps import get_session
        def override_get_session():
            try:
                yield self.session
            finally:
                pass
        
        app.dependency_overrides[get_session] = override_get_session
        
        self.client = TestClient(app)
        yield
        
        app.dependency_overrides.clear()
        self.session.close()
        SQLModel.metadata.drop_all(engine)
    
    def create_test_user(self, username, password, role=Role.USER):
        user = User(
            username=username,
            password_hash=get_password_hash(password),
            role=role,
        )
        self.session.add(user)
        self.session.commit()
        self.session.refresh(user)
        return user
    
    def create_test_brand(self):
        brand = Brand(name="Test Brand")
        self.session.add(brand)
        self.session.commit()
        self.session.refresh(brand)
        return brand
    
    def create_test_category(self):
        category = Category(name="Test Category")
        self.session.add(category)
        self.session.commit()
        self.session.refresh(category)
        return category
    
    def create_test_item(self, name="Test Item", quantity=10):
        brand = self.create_test_brand()
        category = self.create_test_category()
        
        item = Item(
            name=name,
            description="Test Description",
            price=100.0,
            quantity=quantity,
            brand_id=brand.id,
            category_id=category.id,
        )
        self.session.add(item)
        self.session.commit()
        self.session.refresh(item)
        return item
    
    def set_auth_cookies(self, user):
        access_token = create_access_token(user, timedelta(minutes=30))
        self.client.cookies.set("access_token", access_token)
        self.client.cookies.set("role", user.role.value)
    
    def test_successful_item_purchase(self):
        """Тест 1: Проверить успешную покупку товара пользователем"""
        user = self.create_test_user('customer', 'password123', Role.USER)
        test_item = self.create_test_item(quantity=10)
        
        self.set_auth_cookies(user)
        
        mock_notify = AsyncMock()
        
        with patch('api.routs.buy.manager.notify_managers_about_buying', mock_notify):
            purchase_data = {
                "quantity": 2
            }
            
            response = self.client.patch(f"/buy/{test_item.id}", json=purchase_data)
            
            assert response.status_code == 200
            
            item_data = response.json()
            assert item_data["quantity"] == 8
            
            mock_notify.assert_called_once()
            
            call_args = mock_notify.call_args[0]
            assert call_args[0] == "customer"
            assert call_args[1] == "Test Item"
            assert call_args[2] == 2
    
    def test_purchase_nonexistent_item(self):
        """Тест 2: Проверить обработку покупки несуществующего товара"""
        user = self.create_test_user('customer2', 'password123', Role.USER)
        
        self.set_auth_cookies(user)
        
        purchase_data = {
            "quantity": 2
        }
        
        response = self.client.patch("/buy/999", json=purchase_data)
        
        assert response.status_code == 404
        assert response.json()["detail"] == "Товар не найден"
    
    def test_purchase_more_than_available(self):
        """Тест 3: Проверить обработку попытки покупки большего количества, чем есть в наличии"""
        user = self.create_test_user('customer4', 'password123', Role.USER)
        test_item = self.create_test_item(quantity=10)
        
        self.set_auth_cookies(user)
        
        purchase_data = {
            "quantity": 15
        }
        
        response = self.client.patch(f"/buy/{test_item.id}", json=purchase_data)
        
        assert response.status_code == 400
        assert response.json()["detail"] == "Недостаточно товара"
        
        item_in_db = self.session.get(Item, test_item.id)
        assert item_in_db.quantity == 10
    
    def test_purchase_with_manager_role(self):
        """Тест 4: Проверить запрет покупки товара пользователем без прав (не USER)"""
        manager_user = self.create_test_user('manager', 'password123', Role.MANAGER)
        test_item = self.create_test_item()
        
        self.set_auth_cookies(manager_user)
        
        purchase_data = {
            "quantity": 2
        }
        
        response = self.client.patch(f"/buy/{test_item.id}", json=purchase_data)
        
        assert response.status_code == 403
        assert response.json()["detail"] == "Доступ запрещён"

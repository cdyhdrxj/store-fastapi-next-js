import pytest
from fastapi.testclient import TestClient
from datetime import timedelta
from unittest.mock import patch

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

class TestItemIntegration:
    
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
    
    def create_test_brand(self, name="Test Brand"):
        brand = Brand(name=name)
        self.session.add(brand)
        self.session.commit()
        self.session.refresh(brand)
        return brand
    
    def create_test_category(self, name="Test Category"):
        category = Category(name=name)
        self.session.add(category)
        self.session.commit()
        self.session.refresh(category)
        return category
    
    def create_test_item(self, name="Test Item", description="Test Description", price=100.0, quantity=10, category_id=None, brand_id=None):
        if not category_id:
            category = self.create_test_category()
            category_id = category.id
        if not brand_id:
            brand = self.create_test_brand()
            brand_id = brand.id
        
        item = Item(
            name=name,
            description=description,
            price=price,
            quantity=quantity,
            brand_id=brand_id,
            category_id=category_id,
        )
        self.session.add(item)
        self.session.commit()
        self.session.refresh(item)
        return item
    
    def set_auth_cookies(self, user):
        access_token = create_access_token(user, timedelta(minutes=30))
        self.client.cookies.set("access_token", access_token)
        self.client.cookies.set("role", user.role.value)
    
    # Тесты для функции create_item
    def test_create_item_with_manager_role(self):
        """Тест 1: Проверить создание товара пользователем с ролью менеджера"""
        manager_user = self.create_test_user('manager', 'password123', Role.MANAGER)
        brand = self.create_test_brand()
        category = self.create_test_category()
        
        self.set_auth_cookies(manager_user)
        
        item_data = {
            "name": "New Test Item",
            "description": "New Test Description",
            "price": 150.0,
            "brand_id": brand.id,
            "category_id": category.id,
        }
        
        response = self.client.post("/items/", json=item_data)
        
        assert response.status_code == 200
        item_response = response.json()
        assert item_response["name"] == "New Test Item"
        assert item_response["price"] == 150.0
    
    def test_create_item_with_user_role(self):
        """Тест 2: Проверить запрет создания товара пользователем без прав"""
        regular_user = self.create_test_user('user', 'password123', Role.USER)
        brand = self.create_test_brand()
        category = self.create_test_category()
        
        self.set_auth_cookies(regular_user)
        
        item_data = {
            "name": "New Test Item",
            "description": "New Test Description",
            "price": 150.0,
            "brand_id": brand.id,
            "category_id": category.id,
        }
        
        response = self.client.post("/items/", json=item_data)
        
        assert response.status_code == 403
        assert response.json()["detail"] == "Доступ запрещён"
    
    # Тесты для функции read_items
    def test_read_items_with_pagination(self):
        """Тест 3: Проверить получение списка товаров с пагинацией"""
        for i in range(15):
            self.create_test_item(f"Item {i}")
        
        response = self.client.get("/items/?offset=0&limit=10")
        
        assert response.status_code == 200
        data = response.json()
        assert len(data["items"]) == 10
        assert data["total"] == 15
        assert data["pages"] == 2
    
    def test_read_items_with_search(self):
        """Тест 4: Проверить поиск товаров по названию"""
        for i in range(5):
            self.create_test_item(f"Тестовый товар {i}")
        for i in range(10):
            self.create_test_item(f"Другой товар {i}")
        
        response = self.client.get("/items/?search=Тестовый")
        
        assert response.status_code == 200
        data = response.json()
        assert len(data["items"]) == 5
        for item in data["items"]:
            assert "Тестовый" in item["name"]
    
    # Тесты для функции read_item
    def test_read_existing_item(self):
        """Тест 5: Проверить получение существующего товара"""
        test_item = self.create_test_item()
        
        response = self.client.get(f"/items/{test_item.id}")
        
        assert response.status_code == 200
        item_data = response.json()
        assert item_data["id"] == test_item.id
        assert item_data["name"] == test_item.name
    
    def test_read_nonexistent_item(self):
        """Тест 6: Проверить попытку получения несуществующего товара"""
        response = self.client.get("/items/999")
        
        assert response.status_code == 404
        assert response.json()["detail"] == "Товар не найден"
    
    # Тесты для функции update_item
    def test_update_item_with_manager_role(self):
        """Тест 7: Проверить обновление товара менеджером"""
        manager_user = self.create_test_user('manager2', 'password123', Role.MANAGER)
        test_item = self.create_test_item()
        
        self.set_auth_cookies(manager_user)
        
        update_data = {
            "name": "Updated Item Name",
            "price": 200.0
        }
        
        response = self.client.patch(f"/items/{test_item.id}", json=update_data)
        
        assert response.status_code == 200
        item_data = response.json()
        assert item_data["name"] == "Updated Item Name"
        assert item_data["price"] == 200.0
    
    def test_update_item_with_user_role(self):
        """Тест 8: Проверить запрет обновления товара пользователем без прав"""
        regular_user = self.create_test_user('user2', 'password123', Role.USER)
        test_item = self.create_test_item()
        
        self.set_auth_cookies(regular_user)
        
        update_data = {
            "name": "Updated Item Name",
            "price": 200.0
        }
        
        response = self.client.patch(f"/items/{test_item.id}", json=update_data)
        
        assert response.status_code == 403
        assert response.json()["detail"] == "Доступ запрещён"
    
    # Тесты для функции update_quantity
    def test_update_quantity_increase(self):
        """Тест 9: Проверить увеличение количества товара"""
        manager_user = self.create_test_user('manager3', 'password123', Role.MANAGER)
        test_item = self.create_test_item(quantity=10)
        
        self.set_auth_cookies(manager_user)
        
        update_data = {
            "quantity": 5
        }
        
        response = self.client.patch(f"/items/add/{test_item.id}", json=update_data)
        
        assert response.status_code == 200
        item_data = response.json()
        assert item_data["quantity"] == 15
    
    # Тесты для функции delete_item
    def test_delete_item_with_manager_role(self):
        """Тест 10: Проверить удаление товара менеджером"""
        with patch('general.image.image_delete') as mock_delete:
            mock_delete.return_value = True
            
            manager_user = self.create_test_user('manager5', 'password123', Role.MANAGER)
            test_item = self.create_test_item()
            
            self.set_auth_cookies(manager_user)
            
            response = self.client.delete(f"/items/{test_item.id}")
            
            assert response.status_code == 200
            assert response.json() == {"ok": True}
            
            item_in_db = self.session.get(Item, test_item.id)
            assert item_in_db is None
    
    def test_delete_item_with_user_role(self):
        """Тест 11: Проверить запрет удаления товара пользователем без прав"""
        regular_user = self.create_test_user('user3', 'password123', Role.USER)
        test_item = self.create_test_item()
        
        self.set_auth_cookies(regular_user)
        
        response = self.client.delete(f"/items/{test_item.id}")
        
        assert response.status_code == 403
        assert response.json()["detail"] == "Доступ запрещён"
        
        item_in_db = self.session.get(Item, test_item.id)
        assert item_in_db is not None
    
    # Тесты для функции get_similar_items
    def test_get_similar_items_by_category(self):
        """Тест 12: Проверить поиск похожих товаров по категории"""
        category = self.create_test_category("Electronics")
        brand = self.create_test_brand("Sony")
        
        main_item = self.create_test_item(
            name="Sony TV",
            category_id=category.id,
            brand_id=brand.id
        )
        
        for i in range(3):
            self.create_test_item(
                name=f"Similar TV {i}",
                category_id=category.id,
                brand_id=brand.id,
                price=100.0 + i * 50
            )
        
        other_category = self.create_test_category("Books")
        for i in range(3):
            self.create_test_item(
                name=f"Book {i}",
                category_id=other_category.id,
                brand_id=brand.id
            )
        
        response = self.client.get(f"/items/similar/{main_item.id}")
        
        assert response.status_code == 200
        similar_items = response.json()
        assert len(similar_items) == 3
        for item in similar_items:
            assert item["category"]["id"] == category.id
    
    def test_get_similar_items_nonexistent(self):
        """Тест 13: Проверить поиск похожих товаров для несуществующего товара"""
        response = self.client.get("/items/similar/999")
        
        assert response.status_code == 404
        assert response.json()["detail"] == "Товар не найден"

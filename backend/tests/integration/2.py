import pytest
from fastapi.testclient import TestClient
from datetime import datetime, timedelta
import io
from unittest.mock import patch, mock_open, MagicMock

from main import app
from models.user import User
from models.item import Item, Image
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

class TestImageIntegration:
    
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
        brand = Brand(
            name="Test Brand",
        )
        self.session.add(brand)
        self.session.commit()
        self.session.refresh(brand)
        return brand
    
    def create_test_category(self):
        category = Category(
            name="Test Category",
        )
        self.session.add(category)
        self.session.commit()
        self.session.refresh(category)
        return category
    
    def create_test_item(self):
        brand = self.create_test_brand()
        category = self.create_test_category()
        
        item = Item(
            name="Test Item",
            description="Test description",
            price=100.0,
            brand_id=brand.id,
            category_id=category.id,
        )
        self.session.add(item)
        self.session.commit()
        self.session.refresh(item)
        return item
    
    def create_test_image(self, item_id):
        image = Image(
            name="test_image.jpg",
            item_id=item_id
        )
        self.session.add(image)
        self.session.commit()
        self.session.refresh(image)
        return image
    
    def set_auth_cookies(self, user):
        access_token = create_access_token(user, timedelta(minutes=30))
        self.client.cookies.set("access_token", access_token)
        self.client.cookies.set("role", user.role.value)
    
    def create_test_image_file(self):
        jpeg_data = b'0' * 100
        return ("test.jpg", io.BytesIO(jpeg_data), "image/jpeg")
    
    # Тесты для функции create_image

    def test_create_image_with_manager_role(self):
        """Тест 1: Проверить загрузку изображения для товара пользователем с ролью менеджера"""
        mock_config = MagicMock()
        mock_config.UPLOAD_FOLDER = "/mock/upload/folder"
        mock_config.ALLOWED_MIME_TYPE = "image/"
        mock_config.MAX_FILE_SIZE = 5 * 1024 * 1024
        
        with patch('general.image.generate_unique_filename') as mock_generate, \
             patch('builtins.open', mock_open()) as mock_file, \
             patch('os.path.join') as mock_join, \
             patch('general.image.config', mock_config):
            
            mock_generate.return_value = "test_unique_image.jpg"
            mock_join.return_value = "/mock/path/test_unique_image.jpg"
            
            manager_user = self.create_test_user('manager', 'password123', Role.MANAGER)
            test_item = self.create_test_item()
            
            self.set_auth_cookies(manager_user)
            
            files = {'file': self.create_test_image_file()}
            response = self.client.post(f"/items/images/{test_item.id}", files=files)
            
            assert response.status_code == 200
            
            item_data = response.json()
            assert item_data['id'] == test_item.id
            assert len(item_data['images']) == 1

    def test_create_image_with_user_role(self):
        """Тест 2: Проверить запрет загрузки изображения для пользователя без прав"""
        regular_user = self.create_test_user('user', 'password123', Role.USER)
        test_item = self.create_test_item()
        
        self.set_auth_cookies(regular_user)
        
        files = {'file': self.create_test_image_file()}
        response = self.client.post(f"/items/images/{test_item.id}", files=files)
        
        assert response.status_code == 403
        assert response.json()["detail"] == "Доступ запрещён"
    
    def test_create_image_for_nonexistent_item(self):
        """Тест 3: Проверить обработку попытки загрузки изображения для несуществующего товара"""
        with patch('general.image.image_upload') as mock_upload:
            mock_upload.return_value = f"test_image_{datetime.now().timestamp()}.jpg"
            
            manager_user = self.create_test_user('manager2', 'password123', Role.MANAGER)
            
            self.set_auth_cookies(manager_user)
            
            files = {'file': self.create_test_image_file()}
            response = self.client.post("/items/images/999", files=files)
            
            assert response.status_code == 404
            assert response.json()["detail"] == "Товар не найден"

    # Тесты для функции delete_image
    
    def test_delete_image_with_user_role(self):
        """Тест 4: Проверить запрет удаления изображения для пользователя без прав"""
        regular_user = self.create_test_user('user2', 'password123', Role.USER)
        test_item = self.create_test_item()
        test_image = self.create_test_image(test_item.id)
        
        self.set_auth_cookies(regular_user)
        
        response = self.client.delete(f"/items/images/{test_image.id}")
        
        assert response.status_code == 403
        assert response.json()["detail"] == "Доступ запрещён"
        
        image_in_db = self.session.get(Image, test_image.id)
        assert image_in_db is not None
    
    def test_delete_nonexistent_image(self):
        """Тест 5: Проверить обработку попытки удаления несуществующего изображения"""
        manager_user = self.create_test_user('manager4', 'password123', Role.MANAGER)
        
        self.set_auth_cookies(manager_user)
        
        response = self.client.delete("/items/images/999")
        
        assert response.status_code == 404
        assert response.json()["detail"] == "Изображение не найдено"

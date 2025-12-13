import pytest
from fastapi.testclient import TestClient
from datetime import timedelta
import io
import os
import tempfile
import shutil
from unittest.mock import patch

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

class TestImageModulesIntegration:
    
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
        
        self.test_upload_dir = tempfile.mkdtemp()
        
        with patch('config.UPLOAD_FOLDER', self.test_upload_dir):
            with patch('config.ALLOWED_MIME_TYPE', 'image/'):
                with patch('config.MAX_FILE_SIZE', 5 * 1024 * 1024):  # 5MB
                    self.client = TestClient(app)
                    yield
        
        app.dependency_overrides.clear()
        self.session.close()
        SQLModel.metadata.drop_all(engine)
        
        shutil.rmtree(self.test_upload_dir)
    
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
    
    def create_test_image_record(self, item_id, filename="test_image.jpg"):
        image = Image(
            name=filename,
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
    
    def create_valid_image_file(self, size_kb=100):
        """Создать тестовое изображение"""
        image_bytes = b'0' * 100
        return ("test.jpg", io.BytesIO(image_bytes), "image/jpeg")
    
    def create_invalid_file(self):
        """Создать невалидный файл (текстовый)"""
        text_content = b'This is not an image file'
        return ("test.txt", io.BytesIO(text_content), "text/plain")
    
    def create_large_image_file(self):
        """Создать слишком большое изображение (>5MB)"""
        large_content =  b'0' * (6 * 1024 * 1024)  # 6MB
        return ("large.jpg", io.BytesIO(large_content), "image/jpeg")
    
    # Тест 1: Проверить успешную загрузку валидного изображения через интеграцию модулей
    def test_successful_image_upload_integration(self):
        manager_user = self.create_test_user('manager', 'password123', Role.MANAGER)
        test_item = self.create_test_item()
        
        self.set_auth_cookies(manager_user)
        
        files = {'file': self.create_valid_image_file()}
        response = self.client.post(f"/items/images/{test_item.id}", files=files)
        
        assert response.status_code == 200
        
        item_data = response.json()
        assert item_data['id'] == test_item.id
        assert len(item_data['images']) == 1
        
        image_name = item_data['images'][0]['name']
        file_path = os.path.join(self.test_upload_dir, image_name)
        assert os.path.exists(file_path)
        
        assert image_name.startswith('test_')
        assert image_name.endswith('.jpg')
        assert '_' in image_name

    # Тест 2: Проверить обработку невалидного типа файла
    def test_invalid_file_type_rejection(self):
        manager_user = self.create_test_user('manager2', 'password123', Role.MANAGER)
        test_item = self.create_test_item()
        
        self.set_auth_cookies(manager_user)
        
        files = {'file': self.create_invalid_file()}
        response = self.client.post(f"/items/images/{test_item.id}", files=files)
        
        assert response.status_code == 400
        assert response.json()["detail"] == "Файл не является изображением"
        
        assert len(os.listdir(self.test_upload_dir)) == 0
        
        images_in_db = self.session.query(Image).filter(Image.item_id == test_item.id).all()
        assert len(images_in_db) == 0
    
    # Тест 3: Проверить обработку слишком большого файла
    def test_large_file_rejection(self):
        manager_user = self.create_test_user('manager3', 'password123', Role.MANAGER)
        test_item = self.create_test_item()
        
        self.set_auth_cookies(manager_user)
        
        files = {'file': self.create_large_image_file()}
        response = self.client.post(f"/items/images/{test_item.id}", files=files)
        
        assert response.status_code == 400
        assert response.json()["detail"] == "Размер файла более 5 МБ"
        
        assert len(os.listdir(self.test_upload_dir)) == 0
        
        images_in_db = self.session.query(Image).filter(Image.item_id == test_item.id).all()
        assert len(images_in_db) == 0
    
    # Тест 4: Проверить успешное удаление изображения через интеграцию модулей
    def test_successful_image_delete_integration(self):
        manager_user = self.create_test_user('manager4', 'password123', Role.MANAGER)
        test_item = self.create_test_item()
        
        test_filename = "test_delete.jpg"
        test_file_path = os.path.join(self.test_upload_dir, test_filename)
        with open(test_file_path, 'wb') as f:
            f.write(b'test_image_content')
        
        test_image = self.create_test_image_record(test_item.id, test_filename)
        
        self.set_auth_cookies(manager_user)
        
        response = self.client.delete(f"/items/images/{test_image.id}")
        
        assert response.status_code == 200
        assert response.json() == {"ok": True}
        
        assert not os.path.exists(test_file_path)
        
        image_in_db = self.session.get(Image, test_image.id)
        assert image_in_db is None
    
    # Тест 5: Проверить обработку ошибки удаления несуществующего файла
    def test_delete_nonexistent_file_error(self):
        manager_user = self.create_test_user('manager5', 'password123', Role.MANAGER)
        test_item = self.create_test_item()
        
        test_filename = "nonexistent.jpg"
        test_image = self.create_test_image_record(test_item.id, test_filename)
        
        self.set_auth_cookies(manager_user)
        
        response = self.client.delete(f"/items/images/{test_image.id}")
        
        assert response.status_code == 500
        assert response.json()["detail"] == "Невозможно удалить изображение"
        
        image_in_db = self.session.get(Image, test_image.id)
        assert image_in_db is not None

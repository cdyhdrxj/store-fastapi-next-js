import pytest
from fastapi.testclient import TestClient
from datetime import datetime, timedelta
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
from general.image import generate_unique_filename, image_upload, image_delete

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
        """Создать валидное тестовое изображение"""
        image_bytes = b'\xff\xd8\xff\xe0\x00\x10JFIF\x00\x01\x01\x00\x00\x01\x00\x01\x00\x00\xff\xdb\x00C\x00\x08\x06\x06\x07\x06\x05\x08\x07\x07\x07\t\t\x08\n\x0c\x14\r\x0c\x0b\x0b\x0c\x19\x12\x13\x0f\x14\x1d\x1a\x1f\x1e\x1d\x1a\x1c\x1c $.\' ",#\x1c\x1c(7),01444\x1f\'9=82<.342\xff\xc0\x00\x0b\x08\x00\x01\x00\x01\x01\x01\x11\x00\xff\xc4\x00\x1f\x00\x00\x01\x05\x01\x01\x01\x01\x01\x01\x00\x00\x00\x00\x00\x00\x00\x00\x01\x02\x03\x04\x05\x06\x07\x08\t\n\x0b\xff\xc4\x00\xb5\x10\x00\x02\x01\x03\x03\x02\x04\x03\x05\x05\x04\x04\x00\x00\x01}\x01\x02\x03\x00\x04\x11\x05\x12!1A\x06\x13Qa\x07"q\x142\x81\x91\xa1\x08#B\xb1\xc1\x15R\xd1\xf0$3br\x82\t\n\x16\x17\x18\x19\x1a%&\'()*456789:CDEFGHIJSTUVWXYZcdefghijstuvwxyz\x83\x84\x85\x86\x87\x88\x89\x8a\x92\x93\x94\x95\x96\x97\x98\x99\x9a\xa2\xa3\xa4\xa5\xa6\xa7\xa8\xa9\xaa\xb2\xb3\xb4\xb5\xb6\xb7\xb8\xb9\xba\xc2\xc3\xc4\xc5\xc6\xc7\xc8\xc9\xca\xd2\xd3\xd4\xd5\xd6\xd7\xd8\xd9\xda\xe1\xe2\xe3\xe4\xe5\xe6\xe7\xe8\xe9\xea\xf1\xf2\xf3\xf4\xf5\xf6\xf7\xf8\xf9\xfa\xff\xda\x00\x08\x01\x01\x00\x00?\x00\xf8\xeb\xe1\xcf\xc3\xedk\xe2\x97\x8b\xb4\xdf\x0b\xf8~\xd5\xae\xb5\x1b\xe9\x02\x0e\x0e\xc8\x93\xf8\xa4s\xd9Td\x93\xed\xf8W\xec/\xc1\x7f\x85\xbaO\xc1\x7f\x87\xbao\x85\xf4d\x06;\x84\x12\xdd\xdd\x11\x87\xbb\xb8#\xe6\x91\xbf\xa0\xec\x00\x1d\xab\xd0\xe8\xa2\x8a\xff\xd9'
        return ("test.jpg", io.BytesIO(image_bytes), "image/jpeg")
    
    def create_invalid_file(self):
        """Создать невалидный файл (текстовый)"""
        text_content = b'This is not an image file'
        return ("test.txt", io.BytesIO(text_content), "text/plain")
    
    def create_large_image_file(self):
        """Создать слишком большое изображение (>5MB)"""
        large_content = b'\xff\xd8\xff\xe0' + b'0' * (6 * 1024 * 1024)  # 6MB
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

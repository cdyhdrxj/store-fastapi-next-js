import pytest
from unittest.mock import Mock, patch
from fastapi import HTTPException
from general.image import generate_unique_filename, validate_file_type, validate_file_size, image_upload, image_delete
import config

# Модуль работы с изображениями
class TestImage:    
    def test_generate_unique_filename(self):
        """Тест 1: Проверить генерацию уникального имени файла."""
        result = generate_unique_filename("test.jpg", 50)
        
        assert result.endswith(".jpg")
        assert len(result) <= 50
        assert result != "test.jpg"

    def test_generate_unique_filename_max_length(self):
        """Тест 2: Проверить ограничение максимальной длины имени файла"""
        result = generate_unique_filename("очень_длинное_имя_файла.jpg", 20)
        
        assert len(result) <= 20
        assert result.endswith(".jpg")

    def test_validate_file_type_valid(self):
        """Тест 3: Проверить валидацию корректного типа файла."""
        mock_file = Mock()
        mock_file.content_type = "image/jpeg"
        
        result = validate_file_type(mock_file)
        
        assert result == mock_file

    def test_validate_file_type_invalid(self):
        """Тест 4: Проверить валидацию некорректного типа файла"""
        mock_file = Mock()
        mock_file.content_type = "application/pdf"
        
        with pytest.raises(HTTPException) as exc_info:
            validate_file_type(mock_file)
        
        assert exc_info.value.status_code == 400

    def test_validate_file_size_valid(self):
        """Тест 5: Проверить валидацию корректного размера файла."""
        mock_file = Mock()
        mock_file.size = 1048576  # 1MB
        
        result = validate_file_size(mock_file)
        
        assert result == result

    def test_validate_file_size_too_large(self):
        """Тест 6: Проверить валидацию слишком большого файла."""
        mock_file = Mock()
        mock_file.size = 10485760  # 10MB
        
        with pytest.raises(HTTPException) as exc_info:
            validate_file_size(mock_file)
        
        assert exc_info.value.status_code == 400

    @patch('general.image.os.path.join')
    @patch('general.image.open')
    @patch('general.image.generate_unique_filename')
    def test_image_upload_success(self, mock_generate, mock_open, mock_join):
        """Тест 7: Проверить успешную загрузку изображения."""
        mock_file = Mock()
        mock_file.filename = 'test.jpg'
        mock_file.file.read.return_value = b'fake_image_data'
        
        mock_generate.return_value = 'уникальное_имя.jpg'
        mock_join.return_value = '/uploads/уникальное_имя.jpg'
        
        mock_file_buffer = Mock()
        mock_open.return_value.__enter__.return_value = mock_file_buffer
        
        result = image_upload(mock_file)
        
        assert result == 'уникальное_имя.jpg'
        mock_generate.assert_called_once_with('test.jpg')
        mock_join.assert_called_once_with(config.UPLOAD_FOLDER, 'уникальное_имя.jpg')
        mock_open.assert_called_once_with('/uploads/уникальное_имя.jpg', 'wb')
        mock_file_buffer.write.assert_called_once_with(b'fake_image_data')

    @patch('general.image.os.remove')
    def test_image_delete_success(self, mock_remove):
        """Тест 8: Проверить успешное удаление изображения."""
        filename = "test_image.jpg"
        
        image_delete(filename)
        
        mock_remove.assert_called_once()

    @patch('general.image.os.remove')
    def test_image_delete_file_not_found(self, mock_remove):
        """Тест 9: Проверить обработку отсутствующего файла при удалении."""
        mock_remove.side_effect = FileNotFoundError
        
        image_delete("несуществующий_файл.jpg")
        
        mock_remove.assert_called_once()

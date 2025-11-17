import pytest
from unittest.mock import Mock, AsyncMock, patch, MagicMock
from fastapi import HTTPException
from models.item import ItemAdd
from api.routs.buy import buy_item

# Модуль покупки товаров
class TestBuyItem:
    @pytest.mark.asyncio
    async def test_buy_item_success(self):
        """Тест 1: Проверить успешное выполнение покупки товара."""
        mock_session = MagicMock()
        mock_item = MagicMock()
        mock_item.quantity = 5
        mock_item.name = "Смартфон Samsung"
        mock_session.get.return_value = mock_item
        
        mock_user = MagicMock()
        mock_user.username = "иванов_иван"
        
        with patch('api.routs.buy.manager') as mock_manager:
            mock_manager.notify_managers_about_buying = AsyncMock()
            
            result = await buy_item(
                item_id=1,
                item=ItemAdd(quantity=2),
                session=mock_session,
                current_user=mock_user,
                authorize=True
            )
            
            assert result == mock_item

            mock_item.sqlmodel_update.assert_called_once_with({'quantity': 3})
            mock_session.add.assert_called_once_with(mock_item)
            mock_session.commit.assert_called_once()
            mock_session.refresh.assert_called_once_with(mock_item)
            mock_manager.notify_managers_about_buying.assert_called_once_with(
                "иванов_иван", "Смартфон Samsung", 2
            )

    @pytest.mark.asyncio
    async def test_buy_item_not_found(self):
        """Тест 2: Проверить обработку ситуации, когда товар не найден."""
        mock_session = MagicMock()
        mock_session.get.return_value = None
        
        with pytest.raises(HTTPException) as exc_info:
            await buy_item(
                item_id=999,
                item=ItemAdd(quantity=1),
                session=mock_session,
                current_user=MagicMock(),
                authorize=True
            )
        
        assert exc_info.value.status_code == 404
        assert "Товар не найден" in str(exc_info.value.detail)
        mock_session.add.assert_not_called()
        mock_session.commit.assert_not_called()

    @pytest.mark.asyncio
    async def test_buy_item_insufficient_quantity(self):
        """Тест 3: Проверить обработку ситуации, когда запрашиваемое количество больше доступного."""
        mock_session = MagicMock()
        mock_item = MagicMock()
        mock_item.quantity = 1
        mock_session.get.return_value = mock_item
        
        with pytest.raises(HTTPException) as exc_info:
            await buy_item(
                item_id=1,
                item=ItemAdd(quantity=5),
                session=mock_session,
                current_user=MagicMock(),
                authorize=True
            )
        
        assert exc_info.value.status_code == 400
        assert "Недостаточно товара" in str(exc_info.value.detail)
        assert mock_item.quantity == 1
        mock_session.add.assert_not_called()

    @pytest.mark.asyncio
    async def test_buy_item_sqlmodel_update_called(self):
        """Тест 4: Проверить вызов метода обновления данных."""
        mock_session = MagicMock()
        mock_item = MagicMock()
        mock_item.quantity = 5
        mock_item.sqlmodel_update = Mock()
        mock_session.get.return_value = mock_item
        
        with patch('api.routs.buy.manager') as mock_manager:
            mock_manager.notify_managers_about_buying = AsyncMock()
            
            await buy_item(
                item_id=1,
                item=ItemAdd(quantity=2),
                session=mock_session,
                current_user=MagicMock(),
                authorize=True
            )
            
            mock_item.sqlmodel_update.assert_called_once_with({'quantity': 3})

    @pytest.mark.asyncio
    async def test_buy_item_exact_quantity(self):
        """Тест 5: Проверить покупку всего доступного количества товара."""
        mock_session = MagicMock()
        mock_item = MagicMock()
        mock_item.quantity = 3
        mock_item.name = "Наушники"
        mock_session.get.return_value = mock_item
        
        mock_user = MagicMock()
        mock_user.username = "иванов_иван"
        
        with patch('api.routs.buy.manager') as mock_manager:
            mock_manager.notify_managers_about_buying = AsyncMock()
            
            result = await buy_item(
                item_id=1,
                item=ItemAdd(quantity=3),
                session=mock_session,
                current_user=mock_user,
                authorize=True
            )
            
            assert result == mock_item
            mock_item.sqlmodel_update.assert_called_once_with({'quantity': 0})
            mock_manager.notify_managers_about_buying.assert_called_once_with(
                "иванов_иван", "Наушники", 3
            )

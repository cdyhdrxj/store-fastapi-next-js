import pytest
import json
from unittest.mock import Mock, AsyncMock
from general.connection_manager import ConnectionManager
from fastapi import WebSocketDisconnect

# Менеджер подключений
class TestConnectionManager:    
    def test_connection_manager_init(self):
        """Тест 1: Проверить инициализацию менеджера подключений"""
        manager = ConnectionManager()
        
        assert manager.active_connections == []
        assert isinstance(manager.active_connections, list)

    @pytest.mark.asyncio
    async def test_connection_manager_connect(self):
        """Тест 2: Проверить добавление нового подключения"""
        manager = ConnectionManager()
        mock_websocket = AsyncMock()
        
        await manager.connect(mock_websocket)
        
        mock_websocket.accept.assert_called_once()
        assert len(manager.active_connections) == 1
        assert mock_websocket in manager.active_connections

    def test_connection_manager_disconnect(self):
        """Тест 3: Проверить удаление подключения."""
        manager = ConnectionManager()
        mock_websocket = Mock()
        manager.active_connections = [mock_websocket]
        
        manager.disconnect(mock_websocket)
        
        assert len(manager.active_connections) == 0
        assert mock_websocket not in manager.active_connections

    @pytest.mark.asyncio
    async def test_connection_manager_send_message(self):
        """Тест 4: Проверить отправку сообщения конкретному клиенту."""
        manager = ConnectionManager()
        mock_websocket = AsyncMock()
        
        await manager.send_message("тестовое сообщение", mock_websocket)
        
        mock_websocket.send_text.assert_called_once_with("тестовое сообщение")

    @pytest.mark.asyncio
    async def test_connection_manager_broadcast(self):
        """Тест 5: Проверить рассылку сообщений"""
        manager = ConnectionManager()
        mock_websockets = [AsyncMock() for _ in range(3)]
        manager.active_connections = mock_websockets
        
        await manager.broadcast("тестовое сообщение")
        
        for websocket in mock_websockets:
            websocket.send_text.assert_called_once_with("тестовое сообщение")

    @pytest.mark.asyncio
    async def test_connection_manager_broadcast_with_disconnect(self):
        """Тест 6: Проверить обработку отключившихся клиентов при рассылке."""
        manager = ConnectionManager()
        
        good_websocket1 = AsyncMock()
        good_websocket2 = AsyncMock()
        bad_websocket = AsyncMock()
        bad_websocket.send_text.side_effect = WebSocketDisconnect()
        
        await manager.connect(good_websocket1)
        await manager.connect(bad_websocket) 
        await manager.connect(good_websocket2)
        
        await manager.broadcast("тест")
        
        assert bad_websocket not in manager.active_connections
        assert good_websocket1 in manager.active_connections
        assert good_websocket2 in manager.active_connections
        assert len(manager.active_connections) == 2

    @pytest.mark.asyncio
    async def test_connection_manager_notify_managers(self):
        """Тест 7: Проверить формирование уведомления о покупке."""
        manager = ConnectionManager()
        manager.broadcast = AsyncMock()
        
        await manager.notify_managers_about_buying(
            username="иванов_иван",
            item="Ноутбук Asus", 
            quantity=2
        )
        
        manager.broadcast.assert_called_once()
        call_args = manager.broadcast.call_args[0][0]
        message_data = json.loads(call_args)
        
        assert message_data["username"] == "иванов_иван"
        assert message_data["item"] == "Ноутбук Asus"
        assert message_data["quantity"] == 2

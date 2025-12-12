import pytest
import json
from fastapi import WebSocket
from unittest.mock import AsyncMock

from sqlmodel import create_engine
from sqlmodel.pool import StaticPool

DATABASE_URL = "sqlite:///:memory:"

engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)

class TestBuyNotificationIntegration:
    
    @pytest.mark.asyncio
    async def test_buy_item_with_notification_integration(self):
        """Тест 1: Проверить интеграцию покупки товара с отправкой уведомлений"""
        
        from api.deps import manager
        
        mock_manager_websocket = AsyncMock(spec=WebSocket)
        mock_manager_websocket.send_text = AsyncMock()
        
        original_connections = manager.active_connections.copy()
        manager.active_connections = [mock_manager_websocket]
        
        try:
            test_data = {
                "username": "customer",
                "item": "Smartphone",
                "quantity": 1
            }
            
            await manager.notify_managers_about_buying(
                username=test_data["username"],
                item=test_data["item"],
                quantity=test_data["quantity"]
            )
            
            assert mock_manager_websocket.send_text.called
            
            sent_message = mock_manager_websocket.send_text.call_args[0][0]
            message_data = json.loads(sent_message)
            
            assert message_data["username"] == "customer"
            assert message_data["item"] == "Smartphone"
            assert message_data["quantity"] == 1
            
        finally:
            manager.active_connections = original_connections

    @pytest.mark.asyncio
    async def test_buy_item_triggers_notification_to_all_managers(self):
        """Тест 2: Проверить что покупка товара отправляет уведомление всем подключенным менеджерам"""
        
        from api.deps import manager
        
        mock_manager1 = AsyncMock(spec=WebSocket)
        mock_manager1.send_text = AsyncMock()
        
        mock_manager2 = AsyncMock(spec=WebSocket)
        mock_manager2.send_text = AsyncMock()
        
        original_connections = manager.active_connections.copy()
        manager.active_connections = [mock_manager1, mock_manager2]
        
        try:
            await manager.notify_managers_about_buying(
                username="test_user",
                item="Ноутбук",
                quantity=2
            )
            
            assert mock_manager1.send_text.called
            assert mock_manager2.send_text.called
            
            message1 = json.loads(mock_manager1.send_text.call_args[0][0])
            message2 = json.loads(mock_manager2.send_text.call_args[0][0])
            
            assert message1 == message2
            assert message1["username"] == "test_user"
            assert message1["item"] == "Ноутбук"
            assert message1["quantity"] == 2
            
        finally:
            manager.active_connections = original_connections

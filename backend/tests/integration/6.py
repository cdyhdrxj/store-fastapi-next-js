import pytest
from fastapi.testclient import TestClient
from fastapi import WebSocket, WebSocketDisconnect
from datetime import timedelta
from unittest.mock import AsyncMock, MagicMock

from main import app
from models.user import User
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

class TestNotificationIntegration:
    
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
    
    def create_auth_cookie(self, user):
        """Создать cookie для аутентификации"""
        access_token = create_access_token(user, timedelta(minutes=30))
        return {"access_token": access_token, "role": user.role.value}

    @pytest.mark.asyncio
    async def test_websocket_connect_manager(self):
        """Тест 1: Проверить успешное подключение менеджера к WebSocket"""
        manager_user = self.create_test_user('manager', 'password123', Role.MANAGER)
        cookies = self.create_auth_cookie(manager_user)
        
        mock_websocket = AsyncMock(spec=WebSocket)
        mock_websocket.accept = AsyncMock()
        mock_websocket.receive_text = AsyncMock(side_effect=WebSocketDisconnect())
        
        from api.deps import manager as notification_manager
        original_connect = notification_manager.connect
        original_disconnect = notification_manager.disconnect
        
        notification_manager.connect = AsyncMock()
        notification_manager.disconnect = MagicMock()
        
        try:
            from api.routs.websocket import websocket_endpoint
            await websocket_endpoint(mock_websocket, authorize=True)
            
            notification_manager.connect.assert_called_once_with(mock_websocket)
            
        finally:
            notification_manager.connect = original_connect
            notification_manager.disconnect = original_disconnect
    
    def test_websocket_connect_user_forbidden(self):
        """Тест 2: Проверить запрет подключения пользователя без роли менеджера"""
        regular_user = self.create_test_user('user', 'password123', Role.USER)
        
        access_token = create_access_token(regular_user, timedelta(minutes=30))
        cookies = {"access_token": access_token, "role": Role.USER.value}
       
        from fastapi import status, HTTPException
        from general.permission_checker import PermissionChecker
        
        permission_checker = PermissionChecker(roles=[Role.MANAGER])
        
        mock_user = MagicMock()
        mock_user.role = Role.USER
        
        with pytest.raises(HTTPException) as exc_info:
            permission_checker.__call__(mock_user)
        
        assert exc_info.value.status_code == status.HTTP_403_FORBIDDEN
        assert exc_info.value.detail == "Доступ запрещён"

    @pytest.mark.asyncio
    async def test_websocket_multiple_messages_processing(self):
        """Тест 3: Проверить обработку нескольких сообщений подряд в WebSocket"""
        manager_user = self.create_test_user('manager3', 'password123', Role.MANAGER)
        
        mock_websocket = AsyncMock(spec=WebSocket)
        mock_websocket.accept = AsyncMock()
        
        messages_to_send = [
            "message_1",
            "message_2", 
            "message_3",
            "message_4",
            "message_5"
        ]
        
        current_message_index = 0
        
        async def receive_multiple_messages():
            nonlocal current_message_index
            
            if current_message_index >= len(messages_to_send):
                raise WebSocketDisconnect()
            
            message = messages_to_send[current_message_index]
            current_message_index += 1
            return message
        
        mock_websocket.receive_text = AsyncMock(side_effect=receive_multiple_messages)
        
        from api.deps import manager as notification_manager
        original_connect = notification_manager.connect
        original_disconnect = notification_manager.disconnect
        
        notification_manager.connect = AsyncMock()
        notification_manager.disconnect = MagicMock()
        
        received_messages = []
        
        original_receive_text = mock_websocket.receive_text
        
        async def tracked_receive_text():
            result = await original_receive_text()
            if not isinstance(result, type(WebSocketDisconnect())):
                received_messages.append(result)
            return result
        
        mock_websocket.receive_text = AsyncMock(side_effect=tracked_receive_text)
        
        try:
            from api.routs.websocket import websocket_endpoint
            
            await websocket_endpoint(mock_websocket, authorize=True)
            
            notification_manager.connect.assert_called_once_with(mock_websocket)
            notification_manager.disconnect.assert_called_once_with(mock_websocket)
            
            expected_calls = len(messages_to_send) + 1
            assert mock_websocket.receive_text.call_count == expected_calls
            
            assert len(received_messages) == len(messages_to_send)
            for i, msg in enumerate(messages_to_send):
                assert received_messages[i] == msg
            
            for i in range(len(messages_to_send)):
                assert received_messages[i] == f"message_{i+1}"
            
        finally:
            notification_manager.connect = original_connect
            notification_manager.disconnect = original_disconnect
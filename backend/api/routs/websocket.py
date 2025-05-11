from fastapi import APIRouter, Depends, WebSocket, WebSocketDisconnect

from general.auth import Role
from general.permission_checker import PermissionChecker

from api.deps import manager

router = APIRouter(
    tags=["Уведомления"],
)

@router.websocket("/ws")
async def websocket_endpoint(
    websocket: WebSocket,
    authorize: bool = Depends(PermissionChecker(roles=[Role.MANAGER]))
):
    await manager.connect(websocket)
    try:
        while True:
            await websocket.receive_text()
    except WebSocketDisconnect:
        manager.disconnect(websocket)

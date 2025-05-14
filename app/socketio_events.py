from typing import Dict

import socketio
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from app.core.security import decode_access_token
from app.db.sessions import AsyncSessionLocal
from app.models.user import User  # <-- We'll use this for ORM
from app.schemas.messages import MessageCreate
from app.services.chat_service import ChatService

sio = socketio.AsyncServer(
    async_mode="asgi",
    cors_allowed_origins=["*", "http://localhost:8000"],
    logger=True,
    engineio_logger=True
)

connected_users: Dict[int, str] = {}


@sio.event
async def connect(sid, environ, auth):
    token = None

    if auth and 'token' in auth:
        token = auth.get('token')
        print("Token found in auth object:", token)

    if not token:
        print("No token found in any source -> 403")
        return False

    try:
        payload = decode_access_token(token)
        print("payload:", payload)

        if not payload:
            print("decode_access_token -> None -> 403")
            return False

        email = payload.get("sub")
        print("email from token:", email)

        if not email:
            print("No email -> 403")
            return False

        async with AsyncSessionLocal() as db:
            user_id = await get_user_id_by_email(db, email)
        print("found user_id:", user_id)

        if not user_id:
            print("user not found -> 403")
            return False

        connected_users[user_id] = sid
        print(f"User {user_id} (email={email}) connected with sid={sid}")
        return True
    except Exception as e:
        print(f"Error during socket connection: {e}")
        return False


@sio.event
async def disconnect(sid):
    """
    Fired when the client disconnects.
    """
    print(f"[socket.io] disconnect sid={sid}")
    # Remove from connected_users
    for uid, stored_sid in list(connected_users.items()):
        if stored_sid == sid:
            del connected_users[uid]
            break


@sio.on("send_message")
async def handle_send_message(sid, data):
    """
    Receives a message event from the client.
    data example:
    {
      "token": "JWT_TOKEN",   # or rely on 'connect' auth
      "chat_id": 123,
      "text": "Hello from the student"
    }
    """
    print(f"[socket.io] send_message from sid={sid}, data={data}")

    sender_id = get_user_id_by_sid(sid)
    if not sender_id:
        print("Sender not found in connected_users.")
        return

    chat_id = data["chat_id"]
    text = data["text"]

    async with AsyncSessionLocal() as db:
        chat = await ChatService.get_chat_by_id(db, chat_id)
        if not chat:
            print(f"Chat {chat_id} not found.")
            return

        if chat.student_id != sender_id and chat.psychologist_id != sender_id:
            print(f"User {sender_id} is not a participant of chat {chat_id}")
            return

        msg_data = MessageCreate(
            chat_id=chat_id,
            sender_id=sender_id,
            text=text
        )
        saved_msg = await ChatService.save_message(db, msg_data)

        if sender_id == chat.student_id:
            other_user_id = chat.psychologist_id
        else:
            other_user_id = chat.student_id

        recipient_sid = connected_users.get(other_user_id)
        if recipient_sid:
            await sio.emit(
                "new_message",
                {
                    "chat_id": chat_id,
                    "sender_id": sender_id,
                    "text": text,
                    "message_id": saved_msg.id,
                    "created_at": str(saved_msg.created_at)
                },
                room=recipient_sid
            )
        else:
            print(f"User {other_user_id} is offline.")

        await sio.emit(
            "message_sent",
            {
                "status": "ok",
                "message_id": saved_msg.id
            },
            room=sid
        )


async def get_user_id_by_email(db: AsyncSession, email: str) -> int:
    """
    Uses SQLAlchemy ORM to find user_id by email.
    """
    stmt = select(User.id).where(User.email == email)
    result = await db.execute(stmt)
    user_id = result.scalar()
    return user_id


def get_user_id_by_sid(sid: str) -> int:
    """
    Finds user_id by sid in the connected_users dict.
    """
    for uid, stored_sid in connected_users.items():
        if stored_sid == sid:
            return uid
    return None


# Додайте цей код для налагодження CORS
@sio.on("connect_error")
async def handle_connect_error(sid, data):
    print(f"[socket.io] connect_error sid={sid}, data={data}")

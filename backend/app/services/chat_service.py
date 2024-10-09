"""
chat_service.py

Modul ini menyediakan layanan tingkat tinggi untuk operasi terkait chat dalam aplikasi.
Ini bertindak sebagai perantara antara routes dan database manager, menangani logika bisnis
dan penanganan error.

Modul ini menggunakan ChatManager dan KnowledgeBase untuk operasi database,
serta berbagai utilitas untuk autentikasi dan penanganan file.

Fungsi-fungsi dalam modul ini sebagian besar bersifat asynchronous untuk mendukung
operasi non-blocking.
"""

from sqlalchemy.orm import Session
from app.database import ChatManager, KnowledgeBase
from app.models import models
from app import schemas
from typing import List, Optional
from fastapi import UploadFile, HTTPException
import logging
from app.utils.file_utils import save_uploaded_file
from app.api.auth import verify_password, get_password_hash
import os
from anthropic import AsyncAnthropic
from config import Config
import asyncio
from app.utils.feature_utils import Feature
from typing import List, Dict, Any

logger = logging.getLogger(__name__)

CLAUDE_API_KEY = Config.CLAUDE_API_KEY
if not CLAUDE_API_KEY:
    logger.error("CLAUDE_API_KEY is not set")
    raise ValueError("CLAUDE_API_KEY is not set")
MODEL_NAME = Config.MODEL_NAME

chat_manager = ChatManager()
kb = KnowledgeBase()


async def login(db: Session, username: str, password: str) -> Optional[models.User]:
    """
    Mengautentikasi pengguna berdasarkan username dan password.

    Args:
        db (Session): Sesi database SQLAlchemy.
        username (str): Username pengguna.
        password (str): Password pengguna.

    Returns:
        Optional[models.User]: Objek User jika autentikasi berhasil, None jika gagal.

    Raises:
        HTTPException: Jika terjadi kesalahan server internal selama autentikasi.
    """
    try:
        user = await get_user_by_username(db, username)
        if not user or not verify_password(password, user.hashed_password):
            return None
        return user
    except Exception as e:
        logger.error(f"Error authenticating user: {str(e)}")
        raise HTTPException(
            status_code=500, detail="Internal server error during authentication"
        )


async def get_user_by_username(db: Session, username: str) -> Optional[models.User]:
    """
    Mengambil data pengguna berdasarkan username.

    Args:
        db (Session): Sesi database SQLAlchemy.
        username (str): Username pengguna yang dicari.

    Returns:
        Optional[models.User]: Objek User jika ditemukan, None jika tidak ditemukan.

    Raises:
        HTTPException: Jika terjadi kesalahan server internal saat mengambil data pengguna.
    """
    try:
        return chat_manager.get_user(db, username)
    except Exception as e:
        logger.error(f"Error getting user by username: {str(e)}")
        raise HTTPException(
            status_code=500, detail="Internal server error while fetching user"
        )


async def create_user(db: Session, user: schemas.UserCreate) -> models.User:
    """
    Membuat pengguna baru.

    Args:
        db (Session): Sesi database SQLAlchemy.
        user (schemas.UserCreate): Data pengguna untuk dibuat.

    Returns:
        models.User: Objek User yang baru dibuat.

    Raises:
        HTTPException: Jika terjadi kesalahan server internal saat membuat pengguna.
    """
    try:
        hashed_password = get_password_hash(user.password)
        return chat_manager.create_user(db, user.username, hashed_password)
    except Exception as e:
        logger.error(f"Error creating user: {str(e)}")
        raise HTTPException(
            status_code=500, detail="Internal server error while creating user"
        )


async def get_user_chats(db: Session, user_id: int) -> List[Dict[str, Any]]:
    """
    Mengambil daftar chat untuk pengguna tertentu.

    Args:
        db (Session): Sesi database SQLAlchemy.
        user_id (int): ID pengguna.

    Returns:
        List[models.Chat]: Daftar objek Chat milik pengguna.

    Raises:
        HTTPException: Jika terjadi kesalahan server internal saat mengambil daftar chat.
    """
    try:
        chats = chat_manager.get_user_chats(db, user_id)
        return [
            {
                "chat_id": str(chat.id),
                "title": chat.title,
                "created_at": chat.created_at.isoformat(),
                "user_id": str(chat.user_id),
            }
            for chat in chats
        ]
    except Exception as e:
        logger.error(f"Error getting user chats: {str(e)}")
        raise HTTPException(
            status_code=500, detail="Internal server error while fetching user chats"
        )


async def is_first_message(db: Session, chat_id: str) -> bool:
    """
    Memeriksa apakah ini adalah pesan pertama dalam chat.

    Args:
        db (Session): Sesi database SQLAlchemy.
        chat_id (int): ID chat yang akan diperiksa.

    Returns:
        bool: True jika ini adalah pesan pertama, False jika bukan.

    Raises:
        HTTPException: Jika terjadi kesalahan server internal saat memeriksa pesan.
    """
    try:
        messages = await get_chat_messages(db, chat_id)
        return len(messages) == 0
    except Exception as e:
        logger.error(f"Error checking if first message: {str(e)}")
        raise HTTPException(
            status_code=500, detail="Internal server error while checking message"
        )


def get_system_prompt(feature: Feature) -> str:
    """
    Mengembalikan system prompt yang sesuai berdasarkan fitur yang dipilih.

    Args:
        feature (Feature): Fitur yang dipilih untuk chat.

    Returns:
        str: System prompt yang sesuai dengan fitur.
    """
    base_prompt = "Anda adalah asisten AI untuk muatmuat.com. "

    prompts = {
        Feature.GENERAL: base_prompt
        + "Anda mampu menjawab berbagai topik termasuk coding.",
        Feature.CODE_CHECK: base_prompt
        + "Anda akan menilai kesesuaian code dengan standar perusahaan. Standar code perusahaan meliputi: [masukkan standar code perusahaan Anda di sini]",
        Feature.CODE_HELPER: base_prompt
        + "Anda akan membantu menambahkan dokumentasi dan komentar pada code project.",
        Feature.CS_CHATBOT: base_prompt
        + "Anda akan menjawab pertanyaan terkait produk perusahaan berdasarkan informasi dari FAQ.",
    }

    return prompts.get(feature, prompts[Feature.GENERAL])


async def process_chat_message(
    db: Session,
    user_id: str,
    chat_id: str,
    message: str,
    feature: Feature = Feature.GENERAL,
    file_path: Optional[str] = None,
):
    """
    Memproses pesan chat, termasuk menambahkan pesan ke database dan menghasilkan respons AI.

    Args:
        db (Session): Sesi database SQLAlchemy.
        user_id (int): ID pengguna yang mengirim pesan.
        chat_id (int): ID chat tempat pesan dikirim.
        message (str): Isi pesan.
        file_path (Optional[str]): Path file yang diunggah, jika ada.

    Yields:
        str: Respons AI atau pesan error.

    Notes:
        Fungsi ini menggunakan generator untuk streaming respons.
    """
    logger.info(
        f"Processing message for user {user_id}, chat {chat_id}, feature {feature}"
    )
    try:
        if not message and not file_path:
            raise ValueError(
                "Pesan tidak boleh kosong dan tidak ada file yang diunggah"
            )

        # Buat chat baru jika chat_id tidak ada (percakapan baru)
        if chat_id is None:
            logger.info(f"Creating new chat for user {user_id}")
            chat_id = create_new_chat(db, user_id)

        # Logika untuk menentukan judul chat berdasarkan pesan pertama
        if await is_first_message(db, chat_id):
            title = message[:50] + "..." if len(message) > 50 else message
            logger.info(f"First message for chat {chat_id}, updating title")
            await update_chat_title(db, chat_id, title)

        # Ambil riwayat pesan dan cek apakah pesan terakhir adalah dari user
        chat_history = chat_manager.get_chat_messages(db, chat_id)
        if chat_history and chat_history[-1]["is_user"]:
            # Tambahkan placeholder dari assistant jika ada pesan user berturut-turut
            placeholder_response = "I'm processing your previous message."
            chat_manager.add_message(db, chat_id, placeholder_response, is_user=False)

        # Pencarian di knowledge base
        kb_results = kb.search_items(message)
        if kb_results:
            kb_response = kb_results[0]
            response = f"{kb_response.get('answer', '')}"

            if kb_response.get("image_path"):
                response += f"\n {kb_response['image_path']}"

            chat_manager.add_message(db, chat_id, response, is_user=False)
            yield response
            return

        chat_manager.add_message(db, chat_id, message, is_user=True)

        # Jika ada file, baca kontennya
        file_id = None
        file_content = None

        if file_path:
            file_name = os.path.basename(file_path)
            file_size = os.path.getsize(file_path)
            file_info = f"File attached: {file_name} (size: {file_size} bytes)"
            file_id = chat_manager.add_file_to_chat(chat_id, file_name, file_path)
            chat_manager.add_message(
                db, chat_id, file_info, is_user=True, file_id=file_id
            )

        bot_response = ""
        async for chunk in chat_with_retry_stream(
            user_id, chat_id, message, feature, file_content
        ):
            bot_response += chunk
            yield chunk

        # Tambahkan pesan user dan respons dari bot ke riwayat chat
        if bot_response:
            chat_manager.add_message(db, chat_id, bot_response, is_user=False)

    except ValueError as ve:
        logger.error(f"ValueError in process_chat: {str(ve)}")
        yield f"Error: {str(ve)}"

    except Exception as e:
        logger.error(f"Error in process_chat: {str(e)}")
        yield f"Terjadi kesalahan: {str(e)}"


async def chat_with_retry_stream(
    user_id: str,
    chat_id: str,
    message: str,
    feature: Feature = Feature.GENERAL,
    file_content=None,
):
    """
    Mengirim pesan ke Claude API dengan mekanisme retry dan streaming respons.

    Args:
        user_id (str): ID unik pengguna.
        chat_id (int): ID chat.
        message (str): Pesan dari pengguna.
        file_content (Optional): Konten file yang diunggah, jika ada.

    Yields:
        str: Potongan-potongan respons dari model AI.

    Raises:
        Exception: Jika jumlah maksimum percobaan retry tercapai tanpa respons sukses.
    """
    max_retries = 3
    retry_delay = 1

    for attempt in range(max_retries):
        try:
            logger.info(f"Attempt {attempt + 1} for user {user_id}, chat {chat_id}")

            chat_history = await get_chat_messages(Session, chat_id)
            logger.info(f"Retrieved {len(chat_history)} messages from chat history")

            knowledge_base_items = await kb.get_all_items()
            logger.info(
                f"Retrieved {len(knowledge_base_items)} items from knowledge base"
            )

            knowledge_str = "\n".join(
                [
                    f"Q: {item.get('question', '')}\nA: {item.get('answer', '')}"
                    + (
                        f"\nImage: {item.get('image_path', '')}"
                        if item.get("image_path")
                        else ""
                    )
                    for item in knowledge_base_items
                ]
            )

            system_message = (
                get_system_prompt(feature)
                + f"\n\nInformasi tambahan:\n\n{knowledge_str}"
                + """
            Jika pertanyaan tidak terkait dengan informasi di atas, jawab dengan bijak bahwa Anda tidak memiliki informasi tersebut.
            Tidak perlu meminta maaf.
            Kamu tetap harus meyakinkan user bahwa kamu masih bisa menjawab pertanyaan lain"""
            )

            messages = prepare_messages(chat_history, message, file_content)

            async with AsyncAnthropic(api_key=CLAUDE_API_KEY) as client:
                stream = await client.messages.create(
                    model=MODEL_NAME,
                    messages=messages,
                    system=system_message,
                    max_tokens=1000,
                    temperature=0,
                    stream=True,
                )

                async for chunk in stream:
                    if chunk.type == "content_block_delta":
                        yield chunk.delta.text

            logger.info(
                f"Finished processing stream response for user {user_id}, chat {chat_id}"
            )
            return

        except Exception as e:
            logger.error(
                f"Error in API request for user {user_id}: {str(e)}", exc_info=True
            )
            if attempt == max_retries - 1:
                raise
            await asyncio.sleep(retry_delay)
            retry_delay *= 2

    raise Exception("Maximum retry attempts reached without successful response.")


def prepare_messages(chat_history, new_message, file_content=None):
    """
    Menyiapkan pesan untuk dikirim ke API Claude.

    Args:
        chat_history (List[Dict]): Riwayat chat.
        new_message (str): Pesan baru dari pengguna.
        file_content (Optional): Konten file yang diunggah, jika ada.

    Returns:
        List[Dict]: Daftar pesan yang siap dikirim ke API.
    """
    messages = []
    last_role = None
    for msg in chat_history:
        role = "user" if msg["is_user"] else "assistant"
        if role == last_role:
            dummy_role = "assistant" if role == "user" else "user"
            dummy_content = (
                "I understand." if dummy_role == "assistant" else "Please continue."
            )
            messages.append({"role": dummy_role, "content": dummy_content})
        messages.append({"role": role, "content": msg["content"]})
        last_role = role

    if last_role == "user" or last_role is None:
        messages.append(
            {"role": "assistant", "content": "I understand. How can I help you?"}
        )

    user_message_content = [{"type": "text", "text": new_message}]
    if file_content:
        user_message_content.append(file_content)

    messages.append({"role": "user", "content": user_message_content})

    return messages


async def get_chat_messages(db: Session, chat_id: str) -> List[dict]:
    """
    Mengambil semua pesan untuk chat tertentu.

    Args:
        db (Session): Sesi database SQLAlchemy.
        chat_id (int): ID chat yang pesannya akan diambil.

    Returns:
        List[dict]: Daftar pesan dalam format dictionary.

    Raises:
        HTTPException: Jika terjadi kesalahan server internal saat mengambil pesan chat.
    """
    try:
        return chat_manager.get_chat_messages(db, chat_id)
    except Exception as e:
        logger.error(f"Error getting chat messages: {str(e)}")
        raise HTTPException(
            status_code=500, detail="Internal server error while fetching chat messages"
        )


async def create_new_chat(db: Session, user_id: int) -> Dict[str, Any]:
    """
    Membuat chat baru untuk pengguna tertentu.

    Args:
        db (Session): Sesi database SQLAlchemy.
        user_id (int): ID pengguna yang membuat chat.

    Returns:
        models.Chat: Objek Chat yang baru dibuat.

    Raises:
        HTTPException: Jika terjadi kesalahan server internal saat membuat chat baru.
    """
    try:
        new_chat = chat_manager.create_chat(db, user_id)
        return {
            "id": str(new_chat.id),
            "user_id": new_chat.user_id,
            "title": new_chat.title,
            "created_at": new_chat.created_at.isoformat(),
        }
    except Exception as e:
        logger.error(f"Error creating new chat: {str(e)}")
        raise HTTPException(
            status_code=500, detail="Internal server error while creating new chat"
        )


async def add_knowledge_base_item(
    db: Session, question: str, answer: str, image: Optional[UploadFile] = None
) -> dict:
    """
    Menambahkan item baru ke knowledge base.

    Args:
        db (Session): Sesi database SQLAlchemy.
        question (str): Pertanyaan untuk item knowledge base.
        answer (str): Jawaban untuk item knowledge base.
        image (Optional[UploadFile]): File gambar yang diunggah, jika ada.

    Returns:
        dict: Informasi tentang item knowledge base yang baru ditambahkan.

    Raises:
        HTTPException: Jika terjadi kesalahan server internal saat menambahkan item ke knowledge base.
    """
    try:
        image_path = None
        if image:
            image_path = await save_uploaded_file(image)

        return kb.add_item(db, question, answer, image_path)
    except Exception as e:
        logger.error(f"Error adding knowledge base item: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail="Internal server error while adding knowledge base item",
        )


async def update_chat_title(db: Session, chat_id: str, title: str) -> bool:
    """
    Memperbarui judul chat.

    Args:
        db (Session): Sesi database SQLAlchemy.
        chat_id (int): ID chat yang akan diperbarui.
        title (str): Judul baru untuk chat.

    Returns:
        bool: True jika berhasil diperbarui, False jika tidak.

    Raises:
        HTTPException: Jika terjadi kesalahan server internal saat memperbarui judul chat.
    """
    try:
        return chat_manager.update_chat_title(db, chat_id, title)
    except Exception as e:
        logger.error(f"Error updating chat title: {str(e)}")
        raise HTTPException(
            status_code=500, detail="Internal server error while updating chat title"
        )


async def delete_chat(db: Session, chat_id: str) -> bool:
    """
    Menghapus chat berdasarkan ID.

    Args:
        db (Session): Sesi database SQLAlchemy.
        chat_id (int): ID chat yang akan dihapus.

    Returns:
        bool: True jika berhasil dihapus, False jika tidak.

    Raises:
        HTTPException: Jika terjadi kesalahan server internal saat menghapus chat.
    """
    try:
        return chat_manager.delete_chat(db, chat_id)
    except Exception as e:
        logger.error(f"Error deleting chat: {str(e)}")
        raise HTTPException(
            status_code=500, detail="Internal server error while deleting chat"
        )


async def get_latest_chat_id(db: Session, user_id: str) -> Optional[int]:
    """
    Mendapatkan ID chat terbaru untuk pengguna tertentu.

    Args:
        db (Session): Sesi database SQLAlchemy.
        user_id (int): ID pengguna.

    Returns:
        Optional[int]: ID chat terbaru, atau None jika tidak ada.

    Raises:
        HTTPException: Jika terjadi kesalahan server internal saat mengambil ID chat terbaru.
    """
    try:
        return chat_manager.get_latest_chat_id(db, user_id)
    except Exception as e:
        logger.error(f"Error getting latest chat ID: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail="Internal server error while fetching latest chat ID",
        )

import os
from anthropic import AsyncAnthropic
from config import Config
import asyncio
import logging
from typing import List, Dict, Any
from app.database import KnowledgeBase, ChatManager

import json
import base64


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

chat = ChatManager()

CLAUDE_API_KEY = Config.CLAUDE_API_KEY
if not CLAUDE_API_KEY:
    logger.error("CLAUDE_API_KEY is not set")
    raise ValueError("CLAUDE_API_KEY is not set")
MODEL_NAME = Config.MODEL_NAME

try:
    kb = KnowledgeBase()
    logger.info("KnowledgeBase initialized successfully")
except Exception as e:
    logger.error(f"Error initializing KnowledgeBase: {str(e)}", exc_info=True)
    kb = None


async def process_chat_message(
    user_id: str, chat_id: int, message: str, file_path: str = None
):
    """
    Memproses pesan chat dari pengguna dan menghasilkan respons.

    Args:
        user_id (str): ID pengguna yang mengirim pesan.
        chat_id (int): ID chat tempat pesan dikirim.
        message (str): Isi pesan dari pengguna.
    """
    logger.info(f"Processing message for user {user_id}, chat {chat_id}")
    try:
        if not message and not file_path:
            raise ValueError(
                "Pesan tidak boleh kosong dan tidak ada file yang diunggah"
            )

        # Buat chat baru jika chat_id tidak ada (percakapan baru)
        if chat_id is None:
            logger.info(f"Creating new chat for user {user_id}")
            chat_id = kb.create_new_chat(user_id)

        # Logika untuk menentukan judul chat berdasarkan pesan pertama
        if is_first_message(chat_id):
            title = message[:50] + "..." if len(message) > 50 else message
            logger.info(f"First message for chat {chat_id}, updating title")
            update_chat_title(chat_id, title)

        # Ambil riwayat pesan dan cek apakah pesan terakhir adalah dari user
        chat_history = chat.get_chat_messages(chat_id)
        if chat_history and chat_history[-1]["is_user"]:
            # Tambahkan placeholder dari assistant jika ada pesan user berturut-turut
            placeholder_response = "I'm processing your previous message."
            chat.add_message(chat_id, placeholder_response, is_user=False)

        # Pencarian di knowledge base
        kb_results = kb.search_items(message)
        if kb_results:
            kb_response = kb_results[0]
            response = f"{kb_response.get('answer', '')}"

            if kb_response.get("image_path"):
                response += f"\n {kb_response['image_path']}"

            chat.add_message(chat_id, response, is_user=False)
            yield response
            return

        chat.add_message(chat_id, message, is_user=True)

        # Jika ada file, baca kontennya
        file_id = None
        file_content = None

        if file_path:
            file_name = os.path.basename(file_path)
            file_size = os.path.getsize(file_path)
            file_info = f"File attached: {file_name} (size: {file_size} bytes)"
            file_id = chat.add_file_to_chat(chat_id, file_name, file_path)
            chat.add_message(chat_id, file_info, is_user=True, file_id=file_id)

        bot_response = ""
        async for chunk in chat_with_retry_stream(
            user_id, chat_id, message, file_content
        ):
            bot_response += chunk
            yield chunk

        # Tambahkan pesan user dan respons dari bot ke riwayat chat
        if bot_response:
            chat.add_message(chat_id, bot_response, is_user=False)

    except ValueError as ve:
        logger.error(f"ValueError in process_chat: {str(ve)}")
        yield f"Error: {str(ve)}"

    except Exception as e:
        logger.error(f"Error in process_chat: {str(e)}")
        yield f"Terjadi kesalahan: {str(e)}"


async def read_file_content(file_path):
    try:
        with open(file_path, "rb") as file:
            file_content = file.read()
        file_extension = os.path.splitext(file_path)[1].lower()
        if file_extension in [".jpg", ".jpeg", ".png", ".gif"]:
            return {
                "type": "image",
                "source": {
                    "type": "base64",
                    "media_type": f"image/{file_extension[1:]}",
                    "data": base64.b64encode(file_content).decode("utf-8"),
                },
            }
        else:
            return {
                "type": "text",
                "text": file_content.decode("utf-8", errors="ignore"),
            }
    except Exception as e:
        logger.error(f"Error reading file: {str(e)}")
        return None


def get_chat_history(chat_id: int):
    """
    Mengambil riwayat chat.

    Args:
        chat_id (int): ID chat.

    Returns:
        List[Dict[str, any]]: Daftar pesan dalam chat, termasuk informasi file jika ada.
    """
    history = chat.get_chat_history(chat_id)
    for message in history:
        if message.get("file_path"):
            message["file_url"] = f"/uploads/{os.path.basename(message['file_path'])}"
    return history


async def chat_with_retry_stream(
    user_id: str, chat_id: int, message: str, file_content=None
):
    """
    Fungsi untuk mengirim pesan ke Claude API dengan retry dan streaming respons.

    Fungsi ini mengirimkan pesan pengguna ke API Claude, menangani potensi error,
    dan melakukan retry jika diperlukan. Respons dari API distream kembali ke pemanggil.

    Args:
        user_id (str): ID unik pengguna untuk melacak riwayat percakapan.
        message (str): Pesan dari pengguna yang akan dikirim ke API.

    Yields:
        str: Potongan-potongan respons dari model AI, distream secara real-time.

    Raises:
        Exception: Jika jumlah maksimum percobaan retry tercapai tanpa respons sukses.

    Note:
        - Fungsi ini menggunakan riwayat percakapan untuk memberikan konteks ke API.
        - Riwayat percakapan disimpan dengan batasan 10 pesan terakhir.
        - Error seperti RateLimitError, APIError, dll. ditangani dengan retry.
    """
    max_retries = 3
    retry_delay = 1

    for attempt in range(max_retries):
        try:
            logger.info(f"Attempt {attempt + 1} for user {user_id}, chat {chat_id}")

            chat_history = chat.get_chat_messages(chat_id)
            logger.info(f"Retrieved {len(chat_history)} messages from chat history")

            knowledge_base_items = kb.get_all_items()
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

            system_message = f"""Anda adalah asisten AI untuk muatmuat.com. Gunakan informasi berikut untuk menjawab pertanyaan:
            
            {knowledge_str}
            
            Jika pertanyaan tidak terkait dengan informasi di atas, jawab dengan bijak bahwa Anda tidak memiliki informasi tersebut.
            Tidak perlu meminta maaf.
            Kamu tetap harus meyakinkan user bahwa kamu masih bisa menjawab pertanyaan lain"""

            messages = []
            last_role = None
            for msg in chat_history:
                role = "user" if msg["is_user"] else "assistant"
                if role == last_role:
                    # Jika peran sama dengan sebelumnya, tambahkan pesan dummy dari peran lainnya
                    dummy_role = "assistant" if role == "user" else "user"
                    dummy_content = (
                        "I understand."
                        if dummy_role == "assistant"
                        else "Please continue."
                    )
                    messages.append({"role": dummy_role, "content": dummy_content})
                messages.append({"role": role, "content": msg["content"]})
                last_role = role

            # Pastikan pesan terakhir adalah dari assistant sebelum menambahkan pesan user baru
            if last_role == "user" or last_role is None:
                messages.append(
                    {
                        "role": "assistant",
                        "content": "I understand. How can I help you?",
                    }
                )

            user_message_content = [{"type": "text", "text": message}]
            if file_content:
                user_message_content.append(file_content)

            messages.append({"role": "user", "content": user_message_content})
            logger.info(f"Prepared {len(messages)} messages for API request")
            logger.debug(f"Messages: {json.dumps(messages, indent=2)}")

            try:
                async with AsyncAnthropic(api_key=CLAUDE_API_KEY) as client:
                    stream = await client.messages.create(
                        model="claude-3-sonnet-20240229",
                        messages=messages,
                        system=system_message,
                        max_tokens=1000,
                        temperature=0,
                        stream=True,
                    )

                    full_response = ""
                    logger.info(
                        f"Starting to process stream response for user {user_id}, chat {chat_id}"
                    )
                    async for chunk in stream:
                        if chunk.type == "content_block_delta":
                            full_response += chunk.delta.text
                            yield chunk.delta.text

                logger.info(
                    f"Finished processing stream response for user {user_id}, chat {chat_id}"
                )
                return
            except Exception as e:
                logger.error(
                    f"Error in API request for user {user_id}: {str(e)}", exc_info=True
                )
                raise

        except Exception as e:
            logger.error(f"Unhandled error for user {user_id}: {str(e)}", exc_info=True)
            if attempt == max_retries - 1:
                raise
            await asyncio.sleep(retry_delay)
            retry_delay *= 2

    raise Exception("Maximum retry attempts reached without successful response.")


def get_all_chats():
    """
    Mengambil semua chat dari database.

    Returns:
        List[Dict]: Daftar semua chat dengan informasi id, title, dan created_at.
    """
    return chat.get_all_chats()


def get_user_chats(user_id: str):
    return chat.get_user_chats(user_id)


def get_chat_messages(chat_id: int) -> List[Dict[str, Any]]:
    logging.info(f"Fetching messages for chat_id: {chat_id}")
    try:
        messages = chat.get_chat_messages(chat_id)
        logging.info(f"Retrieved {len(messages)} messages for chat_id {chat_id}")
        return messages
    except Exception as e:
        logging.error(
            f"Error fetching messages for chat_id {chat_id}: {str(e)}", exc_info=True
        )
        raise


def create_new_chat(user_id: str):
    return chat.create_new_chat(user_id)


def delte_chat(user_id: str):
    return chat.delte_chat(user_id)


def is_first_message(chat_id: int) -> bool:
    """
    Memeriksa apakah ini adalah pesan pertama dalam chat.
    """
    messages = chat.get_chat_messages(chat_id)
    return len(messages) == 0


def update_chat_title(chat_id: int, title: str):
    """
    Mengupdate judul chat.

    Args:
        chat_id (int): ID chat yang akan diupdate.
        title (str): Judul baru untuk chat.
    """
    return chat.update_chat_title(chat_id, title)

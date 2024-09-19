import os
from anthropic import AsyncAnthropic
from config import Config
import asyncio
import logging
from typing import List, Dict, Any
from knowledge_base import KnowledgeBase
import json

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

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
    Memproses pesan chat dan file yang diunggah.

    Args:
        user_id (str): ID pengguna.
        message (str): Pesan dari pengguna.
        file_path (str, optional): Path file yang diunggah oleh pengguna.

    Yields:
        str: Respons dari model AI sebagai stream.
    """
    logger.info(f"Processing message for user {user_id}, chat {chat_id}")
    try:
        if not message and not file_path:
            raise ValueError(
                "Pesan tidak boleh kosong dan tidak ada file yang diunggah"
            )

        if chat_id is None:
            logger.info(f"Creating new chat for user {user_id}")
            chat_id = kb.create_chat(user_id)

        # Logika untuk menentukan judul chat berdasarkan pesan pertama
        if is_first_message(chat_id):
            title = message[:50] + "..." if len(message) > 50 else message
            logger.info(f"First message for chat {chat_id}, updating title")
            update_chat_title(chat_id, title)

        kb_results = kb.search_items(message)
        if kb_results:
            kb_response = kb_results[0]
            response = f"{kb_response.get('answer', '')}"

            if kb_response.get("image_path"):
                response += f"\n {kb_response['image_path']}"

            kb.add_message(chat_id, response, is_user=False)
            yield response
            return

        file_info = None
        if file_path:
            logger.info(f"Processing file: {file_path}")
            file_name = os.path.basename(file_path)
            file_size = os.path.getsize(file_path)
            file_info = f"File attached: {file_name} (size: {file_size} bytes)"
            kb.add_file_to_chat(chat_id, file_name, file_path)

        full_message = f"{message}\n\n{file_info}" if file_info else message

        logger.info(
            f"Starting chat with retry stream for user {user_id}, chat {chat_id}"
        )
        bot_response = ""
        async for chunk in chat_with_retry_stream(user_id, chat_id, full_message):
            bot_response += chunk
            yield chunk

        if bot_response:
            logger.info(f"Adding user message to chat {chat_id}")
            kb.add_message(chat_id, full_message, is_user=True)
            logger.info(f"Adding bot response to chat {chat_id}")
            kb.add_message(chat_id, bot_response, is_user=False)

    except ValueError as ve:
        logger.error(f"ValueError in process_chat: {str(ve)}")
        yield f"Error: {str(ve)}"

    except Exception as e:
        logger.error(f"Error in process_chat: {str(e)}")
        yield f"Terjadi kesalahan: {str(e)}"


def get_chat_history(chat_id: int):
    """
    Mengambil riwayat chat.

    Args:
        chat_id (int): ID chat.

    Returns:
        List[Dict[str, any]]: Daftar pesan dalam chat, termasuk informasi file jika ada.
    """
    history = kb.get_chat_history(chat_id)
    for message in history:
        if message.get("file_path"):
            message["file_url"] = f"/uploads/{os.path.basename(message['file_path'])}"
    return history


async def chat_with_retry_stream(user_id: str, chat_id: int, message: str):
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

            chat_history = kb.get_chat_messages(chat_id)
            logger.info(f"Retrieved {len(chat_history)} messages from chat history")

            knowledge_base_items = kb.get_all_items()
            logger.info(
                f"Retrieved {len(knowledge_base_items)} items from knowledge base"
            )

            knowledge_str = ""
            if knowledge_base_items:
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
                if role == last_role == "user":
                    # Jika ada dua pesan user berturut-turut, tambahkan pesan kosong dari assistant
                    messages.append(
                        {
                            "role": "assistant",
                            "content": "I'm processing your previous message.",
                        }
                    )
                messages.append({"role": role, "content": msg["content"]})
                last_role = role

            # Pastikan pesan terakhir adalah dari user
            if not messages or messages[-1]["role"] != "user":
                messages.append({"role": "user", "content": message})
            elif message and messages[-1]["content"] != message:
                # Jika pesan baru berbeda dari pesan terakhir, tambahkan sebagai pesan baru
                messages.append({"role": "user", "content": message})

            logger.info(f"Prepared {len(messages)} messages for API request")
            logger.debug(f"Messages: {json.dumps(messages, indent=2)}")

            try:
                async with AsyncAnthropic(api_key=CLAUDE_API_KEY) as client:
                    stream = await client.messages.create(
                        model="claude-3-sonnet-20240229",
                        messages=messages,
                        system=system_message,  # Gunakan system_message sebagai parameter terpisah
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
    return kb.get_all_chats()


def get_user_chats(user_id: str):
    return kb.get_user_chats(user_id)


def get_chat_messages(chat_id: int) -> List[Dict[str, Any]]:
    logging.info(f"Fetching messages for chat_id: {chat_id}")
    try:
        messages = kb.get_chat_messages(chat_id)
        logging.info(f"Retrieved {len(messages)} messages for chat_id {chat_id}")
        return messages
    except Exception as e:
        logging.error(
            f"Error fetching messages for chat_id {chat_id}: {str(e)}", exc_info=True
        )
        raise


def create_new_chat(user_id: str):
    return kb.create_new_chat(user_id)


def is_first_message(chat_id: int) -> bool:
    """
    Memeriksa apakah ini adalah pesan pertama dalam chat.
    """
    messages = kb.get_chat_messages(chat_id)
    return len(messages) == 0


def update_chat_title(chat_id: int, title: str):
    """
    Mengupdate judul chat.

    Args:
        chat_id (int): ID chat yang akan diupdate.
        title (str): Judul baru untuk chat.
    """
    return kb.update_chat_title(chat_id, title)

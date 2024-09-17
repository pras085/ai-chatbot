import os
import anthropic
from anthropic import AsyncAnthropic
from config import Config
import asyncio
import logging
from typing import List, Dict, Any
from knowledge_base import KnowledgeBase

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

CLAUDE_API_KEY = Config.CLAUDE_API_KEY
MODEL_NAME = Config.MODEL_NAME

kb = KnowledgeBase()
conversation_history: Dict[str, List[Dict[str, str]]] = {}


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
    try:
        if not message and not file_path:
            raise ValueError(
                "Pesan tidak boleh kosong dan tidak ada file yang diunggah"
            )

        if chat_id is None:
            chat_id = kb.create_chat(user_id)

        # Logika untuk menentukan judul chat berdasarkan pesan pertama
        if is_first_message(chat_id):
            title = message[:50] + "..." if len(message) > 50 else message
            update_chat_title(chat_id, title)

        file_info = None
        if file_path:
            file_name = os.path.basename(file_path)
            file_size = os.path.getsize(file_path)
            file_info = f"File attached: {file_name} (size: {file_size} bytes)"
            kb.add_file_to_chat(chat_id, file_name, file_path)

        full_message = f"{message}\n\n{file_info}" if file_info else message

        kb.add_message(chat_id, full_message, True)
        async for chunk in chat_with_retry_stream(user_id, full_message):
            yield chunk

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


async def chat_with_retry_stream(user_id: str, message: str):
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
            user_history = conversation_history.get(user_id, [])
            knowledge_base = kb.get_all_items()
            if not knowledge_base:
                logger.warning("Knowledge base is empty. Consider adding some data.")

            system_message = """Anda adalah asisten AI untuk muatmuat.com. Gunakan informasi berikut untuk menjawab pertanyaan:
            
            {knowledge_base}
            
            Jika pertanyaan tidak terkait dengan informasi di atas, jawab dengan bijak bahwa Anda tidak memiliki informasi tersebut.
            Tidak perlu meminta maaf.
            Kamu tetap harus meyakinkan user bahwa kamu masih bisa menjawab pertanyaan lain"""

            knowledge_str = "\n".join(
                [
                    f"Q: {item['question']}\nA: {item['answer']}"
                    for item in knowledge_base
                ]
            )

            messages = [
                *user_history,
                {"role": "user", "content": message},
            ]

            async with AsyncAnthropic(api_key=CLAUDE_API_KEY) as client:
                stream = await client.messages.create(
                    model="claude-3-sonnet-20240229",
                    messages=messages,
                    system=system_message.format(knowledge=knowledge_str),
                    max_tokens=1000,
                    temperature=0,
                    stream=True,
                )

                full_response = ""
                logger.info(f"RESP :::  {stream}")
                async for chunk in stream:
                    if chunk.type == "content_block_delta":
                        full_response += chunk.delta.text
                        yield chunk.delta.text

            user_history.append({"role": "user", "content": message})
            user_history.append({"role": "assistant", "content": full_response})
            conversation_history[user_id] = user_history[
                -10:
            ]  # Simpan 10 pesan terakhir

            # Simpan respons bot ke database
            try:
                # Kode yang mungkin menyebabkan error
                chat_id = kb.get_latest_chat_id(user_id)
            except AttributeError:
                logger.error("Method get_latest_chat_id not found in KnowledgeBase")
                chat_id = None  # Atau gunakan nilai default yang sesuai
                kb.add_message(chat_id, full_response, False)
            return
        except (
            anthropic.RateLimitError,
            anthropic.APIError,
            anthropic.APIConnectionError,
            anthropic.BadRequestError,
        ) as e:
            logger.warning(
                f"Error for user {user_id} on attempt {attempt + 1}: {str(e)}"
            )
            if attempt == max_retries - 1:
                raise
            await asyncio.sleep(retry_delay)
            retry_delay *= 2
        except Exception as e:
            logger.error(f"Unhandled error for user {user_id}: {str(e)}")
            raise

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

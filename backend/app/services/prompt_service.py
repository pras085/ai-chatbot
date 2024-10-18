import asyncio
import json
from typing import Optional, List, Dict
from uuid import UUID
from anthropic import AsyncAnthropic
from sqlalchemy.orm import Session
from starlette.responses import StreamingResponse
from app.config.database import SessionLocal
from app.repositories.context_manager import context_manager
from app.repositories.prompt_logs_manager import prompt_logs_manager
from app.services.new_chat_service import create_new_chat, is_first_message, update_chat_title, chat_manager, \
    get_chat_messages, CLAUDE_API_KEY, MODEL_NAME
from app.services.knowledge_base_service import logger, kb
from app.utils.feature_utils import Feature

async def process_chat_message(
    db: Session,
    user_id: int,
    chat_id: UUID,
    message: str,
    feature: Feature = Feature.GENERAL,
    file_contents: Optional[List[Dict[str, str]]] = None,
):
    async def event_generator():
        nonlocal chat_id
        try:
            if not message and not file_contents:
                raise ValueError(
                    "Pesan tidak boleh kosong dan tidak ada file yang diunggah"
                )

            if chat_id is None:
                chat_id = create_new_chat(db, user_id, feature)

            if await is_first_message(chat_id):
                title = message[:50] + "..." if len(message) > 50 else message
                await update_chat_title(db, chat_id, title)

            chat_history = chat_manager.get_chat_messages(db, chat_id)
            if chat_history and chat_history[-1]["is_user"]:
                placeholder_response = "I'm processing your previous message."
                chat_manager.add_message(
                    db, chat_id, placeholder_response, is_user=False
                )

            # Menambahkan informasi file ke pesan chat
            if file_contents:
                for file in file_contents:
                    file_info = f"File attached: {file['name']}"
                    chat_manager.add_message(db, chat_id, file_info, is_user=True)

            bot_response = ""
            async for chunk in chat_with_retry_stream(
                user_id, chat_id, message, feature, file_contents
            ):
                bot_response += chunk
                yield f"data: {json.dumps({'type': 'message', 'content': chunk})}\n\n"

            if bot_response:
                chat_manager.add_message(db, chat_id, bot_response, is_user=False)

            yield f"data: {json.dumps({'type': 'done'})}\n\n"

        except ValueError as ve:
            logger.error(f"ValueError in process_chat: {str(ve)}")
            yield f"data: {json.dumps({'type': 'error', 'content': str(ve)})}\n\n"
        except Exception as e:
            logger.error(f"Error in process_chat: {str(e)}")
            yield f"data: {json.dumps({'type': 'error', 'content': str(e)})}\n\n"

    return StreamingResponse(event_generator(), media_type="text/event-stream")


async def chat_with_retry_stream(
    user_id: int,
    chat_id: UUID,
    message: str,
    feature: Feature = Feature.GENERAL,
    file_contents: Optional[List[Dict[str, str]]] = None,
):
    """
    Mengirim pesan ke Claude API dengan mekanisme retry dan streaming respons.

    Args:
        file_contents:
        feature:
        user_id (str): ID unik pengguna.
        chat_id (int): ID chat.
        message (str): Pesan dari pengguna.
        file_contents (Optional): Konten file yang diunggah, jika ada.

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

            chat_history = await get_chat_messages(chat_id)
            logger.info(f"Retrieved {len(chat_history)} messages from chat history")

            db = SessionLocal()
            try:
                base_prompt = "Anda adalah asisten AI untuk muatmuat.com, hanya diizinkan menjawab pertanyaan tentang pemrograman, logika pemrograman, serta profil perusahaan muatmuat.com. Pertanyaan di luar topik ini tidak akan dijawab. Anda diizinkan menyajikan gambar yang relevan dengan topik"

                if feature == Feature.GENERAL:
                    system_message = base_prompt + """
                    Anda dapat menjawab pertanyaan terkait pemrograman, logika pemrograman, dan profil muatmuat.com.
                    Untuk pertanyaan tentang standar code perusahaan, arahkan ke fitur Code Check.
                    Untuk dokumentasi code, arahkan ke fitur Code Helper.
                    Untuk pertanyaan produk dan profil muatmuat.com, arahkan ke fitur CS Chatbot.
                    """

                elif feature == Feature.CODE_CHECK:
                    system_message = base_prompt + """
                    Anda akan mengevaluasi apakah kode sesuai dengan standar perusahaan.
                    Untuk file javascript
                    1. nama class harus pascal case.
                    2. nama fungsi harus camel case
                    3. semua komponen  berbahasa inggris. 
                    Untuk file python
                    1. nama class harus pascal case
                    2. nama fungsi harus snake case
                    3. nama variabel harus snake case
                    4. semua komponen berbahasa inggris
                    Untuk dokumentasi code, arahkan ke fitur Code Helper.
                    Untuk pertanyaan umum, arahkan ke fitur General.
                    Untuk pertanyaan tentang profil perusahaan, arahkan ke fitur CS Chatbot.
                    """

                elif feature == Feature.CODE_HELPER:
                    system_message = base_prompt + """
                    Anda akan membantu menambahkan komentar dokumentasi pada kode secara rinci.
                    Untuk pertanyaan umum, arahkan ke fitur General.
                    Untuk evaluasi kesesuaian kode, arahkan ke fitur Code Check.
                    Untuk pertanyaan tentang profil perusahaan, arahkan ke fitur CS Chatbot.
                    """

                elif feature == Feature.CS_CHATBOT:
                    knowledge_base_items = kb.get_all_items(db)
                    knowledge_str = "\n".join(
                        [f"Q: {item.get('question', '')}\nA: {item.get('answer', '')}" for item in knowledge_base_items]
                    )
                    system_message = base_prompt + """
                    Anda akan menjawab pertanyaan terkait produk dan layanan dari muatmuat.com. Berikut FAQ yang tersedia:\n""" + knowledge_str + """
                    Untuk pertanyaan umum, arahkan ke fitur General.
                    Untuk evaluasi kode, arahkan ke fitur Code Check.
                    Untuk dokumentasi kode, arahkan ke fitur Code Helper.
                    Anda tidak perlu memberikan bahwa informasi yang tersedia dalam FAQ, seolah anda memang mengetahuinya.
                    """

                else:
                    raise ValueError(f"Invalid feature: {feature}")

                # contexts are applied for all features
                context = context_manager.get_latest_context(db, user_id)
                logger.info(f"Fetching context for user_id: {user_id}")
                logger.info(f"DB session: {db}")
                if context:
                    system_message += f"\n\nBerikut ini adalah konteks tambahan:"
                    for c in context:
                        if c.content_type == "text":
                            system_message += f"\n{c.content}"
                        elif c.content_type == "file":
                            system_message += (
                                f"\n\nBerikut ini adalah konteks tambahan dari file: \n{c.content_raw}"
                            )

                # Menambahkan file_contents ke dalam pesan jika ada
                if file_contents:
                    for i, file_content in enumerate(file_contents):
                        system_message += f"\n\nFile {i+1} content:\n{file_content}"

                system_message += """
                Jika pertanyaan tidak terkait dengan informasi di atas, jawab dengan bijak bahwa Anda tidak memiliki informasi tersebut.
                Tidak perlu meminta maaf.
                Kamu tetap harus meyakinkan user bahwa kamu masih bisa menjawab pertanyaan lain"""

                # Menambahkan konteks dari file
                if file_contents:
                    system_message += "\n\nAttached files content:\n"
                    for file in file_contents:
                        system_message += f"\nFile: {file['name']}\nContent:\n{file['content'][:1000]}...\n"

                # Building messages
                messages = prepare_messages(chat_history, message, file_contents)

                # Adding prompt logs
                prompt_logs_manager.add_prompt_logs(db, user_id, str(messages), system_message)

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
            finally:
                db.close()  # Pastikan untuk menutup session repositories

        except Exception as e:
            logger.error(
                f"Error in API request for user {user_id}: {str(e)}", exc_info=True
            )
            if attempt == max_retries - 1:
                raise
            await asyncio.sleep(retry_delay)
            retry_delay *= 2

    raise Exception("Maximum retry attempts reached without successful response.")


def prepare_messages(chat_history, new_message, file_contents: Optional[List[Dict[str, str]]]=None):
    """
    Menyiapkan pesan untuk dikirim ke API Claude.

    Args:
        chat_history (List[Dict]): Riwayat chat.
        new_message (str): Pesan baru dari pengguna.
        file_contents (Optional): Konten file yang diunggah, jika ada.

    Returns:
        List[Dict]: Daftar pesan yang siap dikirim ke API.
    """
    # untuk menampung urutan message dalam chat
    messages = []
    # untuk menentukan last role
    last_role = None
    # untuk menyusun message
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
    # Jika ada file_contents, tambahkan ke pesan
    if file_contents:
        for file in file_contents:
            user_message_content.append(
                {
                    "type": "text",
                    "text": f"File: {file['name']}\nContent: {file['content'][:1000]}...",
                }
            )
    messages.append({"role": "user", "content": user_message_content})
    return messages

import asyncio
import json
from typing import Optional, List, Dict
from uuid import UUID

from anthropic import AsyncAnthropic
from sqlalchemy.orm import Session
from starlette.responses import StreamingResponse

from app.repositories.database import SessionLocal
from app.repositories.prompt_logs_manager import prompt_logs_manager

from app.services.new_chat_service import create_new_chat, is_first_message, update_chat_title, chat_manager, kb, \
    logger, get_chat_messages, CLAUDE_API_KEY, MODEL_NAME
from app.utils.feature_utils import Feature


def get_system_prompt(feature: Feature) -> str:
    """
    Mengembalikan system prompt yang sesuai berdasarkan fitur yang dipilih.

    Args:
        feature (Feature): Fitur yang dipilih untuk chat.

    Returns:
        str: System prompt yang sesuai dengan fitur.
    """
    base_prompt = "Anda adalah asisten AI untuk muatmuat.com. Anda hanya diizinkan untuk menjawab pertanyaan seputar pemrograman dan seputar profil perusahaan muatmuat.com"

    prompts = {
        Feature.GENERAL: base_prompt
        + "Anda mampu menjawab berbagai topik termasuk coding. Anda tidak diizinkan untuk menjawab pertanyaan selain masalah pemrograman.",
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

            kb_results = kb.search_items(db, message)
            if kb_results:
                kb_response = kb_results[0]
                response = f"{kb_response.get('answer', '')}"
                if kb_response.get("image_path"):
                    response += f"\n {kb_response['image_path']}"
                chat_manager.add_message(db, chat_id, response, is_user=False)
                yield f"data: {json.dumps({'type': 'message', 'content': response})}\n\n"
                yield f"data: {json.dumps({'type': 'done'})}\n\n"
                return

            chat_manager.add_message(db, chat_id, message, is_user=True)

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

            chat_history = await get_chat_messages(chat_id)
            logger.info(f"Retrieved {len(chat_history)} messages from chat history")

            db = SessionLocal()
            try:
                knowledge_base_items = kb.get_all_items(db)
                logger.info(
                    f"Retrieved {len(knowledge_base_items)} items from knowledge base"
                )

                knowledge_str = "\n".join(
                    [
                        f"Q: {item.get('question', '')}\nA: {item.get('answer', '')}"
                        for item in knowledge_base_items
                    ]
                )

                system_message = (
                    get_system_prompt(feature)
                    + f"\n\nInformasi tambahan:\n\n{knowledge_str}"
                )

                context = kb.get_latest_context(db, user_id)
                logger.info(f"Fetching context for user_id: {user_id}")
                logger.info(f"DB session: {db}")
                if context:
                    system_message += f"\n\nAdditional context:"
                    for c in context:
                        if c.content_type == "text":
                            system_message += f"\n{c.content}"
                        elif c.content_type == "file":
                            system_message += (
                                f"\n\nAdditional context from file: \n{c.content_raw}"
                            )

                # Menambahkan file_contents ke dalam pesan jika ada
                if file_contents:
                    for i, file_content in enumerate(file_contents):
                        system_message += f"\n\nFile {i+1} content:\n{file_content}"

                system_message += """
                \nJika pertanyaan tidak terkait dengan informasi di atas, jawab dengan bijak bahwa Anda tidak memiliki informasi tersebut.
                \nTidak perlu meminta maaf.
                \nKamu tetap harus meyakinkan user bahwa kamu masih bisa menjawab pertanyaan lain"""
                # Menambahkan konteks dari file
                if file_contents:
                    system_message += "\n\nAttached files content:\n"
                    for file in file_contents:
                        system_message += f"\nFile: {file['name']}\nContent:\n{file['content'][:1000]}...\n"

                messages = prepare_messages(chat_history, message, file_contents)

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
                prompt_logs_manager.add_prompt_logs(db, user_id, str(messages), system_message)
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


def prepare_messages(chat_history, new_message, file_contents=None):
    """
    Menyiapkan pesan untuk dikirim ke API Claude.

    Args:
        chat_history (List[Dict]): Riwayat chat.
        new_message (str): Pesan baru dari pengguna.
        file_contents (Optional): Konten file yang diunggah, jika ada.

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

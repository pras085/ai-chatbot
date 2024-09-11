import anthropic
from anthropic import AsyncAnthropic
from config import Config
import asyncio
import logging
from typing import Dict, List

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

CLAUDE_API_KEY = Config.CLAUDE_API_KEY
MODEL_NAME = Config.MODEL_NAME


conversation_history: Dict[str, List[Dict[str, str]]] = {}


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
            messages = user_history + [{"role": "user", "content": message}]

            async with AsyncAnthropic(api_key=CLAUDE_API_KEY) as client:
                stream = await client.messages.create(
                    model="claude-3-sonnet-20240229",
                    messages=messages,
                    max_tokens=1000,
                    temperature=0.2,
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

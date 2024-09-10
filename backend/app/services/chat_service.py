from anthropic import AsyncAnthropic, RateLimitError, APIError, APIConnectionError
import os
import asyncio
import logging

# Konfigurasi logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

CLAUDE_API_KEY = os.getenv("CLAUDE_API_KEY")

conversation_history = {}


async def chat_with_retry_stream(user_id: str, message: str):
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
                async for chunk in stream:
                    if chunk.type == "content_block_delta":
                        full_response += chunk.delta.text
                        yield chunk.delta.text

            user_history.append({"role": "user", "content": message})
            user_history.append({"role": "assistant", "content": full_response})
            conversation_history[user_id] = user_history[
                -10:
            ]  # Simpan 10 pesan terakhir
            logger.info(f"Resp : {full_response}")
            return
        except (RateLimitError, APIError, APIConnectionError) as e:
            logger.warning(
                f"Error for user {user_id} on attempt {attempt + 1}: {str(e)}"
            )
            if attempt == max_retries - 1:
                raise
            await asyncio.sleep(retry_delay)
            retry_delay *= 2
        except Exception as e:
            raise e
    raise Exception("Maksimal percobaan mencapai batas.")

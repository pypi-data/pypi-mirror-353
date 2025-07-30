import asyncio
import os
from datetime import datetime

import dotenv
from dify_client import AsyncDifyClient, DifyClient, models


dotenv.load_dotenv()

DIFY_ENDPOINT = os.getenv("DIFY_ENDPOINT")
DIFY_AVATAR_API_KEY = os.getenv("AVATAR_DIFY_KEY__BOYFRIEND_SOTA_JP")

client = DifyClient(
    api_base=DIFY_ENDPOINT,
    api_key=DIFY_AVATAR_API_KEY,
)

async_client = AsyncDifyClient(
    api_base=DIFY_ENDPOINT,
    api_key=DIFY_AVATAR_API_KEY,
)

user = "user_test_1"

inputs = {
    "language": "japanese",
    "username": "Lucas",
}

user_messages = [
    "こんにちは、私は赤色が好きです。",
    "僕が何色が好きか覚えてる？",
]


def test_sync_blocking_chat():
    conversation_id = ""
    for user_message in user_messages:
        # Create a blocking chat request
        inputs["user_current_time"] = datetime.now().strftime(
            "%Y-%m-%d %H:%M:%S"
        )
        blocking_chat_req = models.ChatRequest(
            query=user_message,
            inputs=inputs,
            user=user,
            response_mode=models.ResponseMode.BLOCKING,
            conversation_id=conversation_id,
        )

        # Send the chat message
        chat_response = client.chat_messages(blocking_chat_req, timeout=60.0)
        print(chat_response)
        conversation_id = chat_response.conversation_id


def test_sync_streaming_chat():
    conversation_id = ""
    for user_message in user_messages:
        inputs["user_current_time"] = datetime.now().strftime(
            "%Y-%m-%d %H:%M:%S"
        )
        streaming_chat_req = models.ChatRequest(
            query=user_message,
            inputs=inputs,
            user=user,
            response_mode=models.ResponseMode.STREAMING,
            conversation_id=conversation_id,
        )

        # Send the chat message
        for chunk in client.chat_messages(streaming_chat_req, timeout=60.0):
            print(chunk)


async def test_async_blocking_chat():
    conversation_id = ""
    for user_message in user_messages:
        inputs["user_current_time"] = datetime.now().strftime(
            "%Y-%m-%d %H:%M:%S"
        )
        blocking_chat_req = models.ChatRequest(
            query=user_message,
            inputs=inputs,
            user=user,
            response_mode=models.ResponseMode.BLOCKING,
            conversation_id=conversation_id,
        )

        chat_response = await async_client.achat_messages(
            blocking_chat_req, timeout=60.0
        )
        print(chat_response)
        conversation_id = chat_response.conversation_id


async def test_async_streaming_chat():
    conversation_id = ""
    for user_message in user_messages:
        inputs["user_current_time"] = datetime.now().strftime(
            "%Y-%m-%d %H:%M:%S"
        )
        streaming_chat_req = models.ChatRequest(
            query=user_message,
            inputs=inputs,
            user=user,
            response_mode=models.ResponseMode.STREAMING,
            conversation_id=conversation_id,
        )

        async for chunk in await async_client.achat_messages(
            streaming_chat_req, timeout=60.0
        ):
            print(chunk)


if __name__ == "__main__":
    # test_sync_blocking_chat()
    # test_sync_streaming_chat()
    # asyncio.run(test_async_blocking_chat())
    asyncio.run(test_async_streaming_chat())

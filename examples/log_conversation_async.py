import asyncio

import getcontext.generated.aio as getcontext
from getcontext.generated.models import Conversation, Message, MessageRole, Rating
from getcontext.token import AsyncCredential
import os

token = os.environ.get("GETCONTEXT_TOKEN")


async def log():
    async with getcontext.ContextAPI(credential=AsyncCredential(token)) as client:
        await client.log.conversation(
            body={
                "conversation": Conversation(
                    messages=[
                        Message(
                            message="You are a helpful assistant!",
                            role=MessageRole.SYSTEM,
                        ),
                        Message(
                            message="Hello, world!",
                            role=MessageRole.USER,
                        ),
                        Message(
                            message="Hi, how can I help?",
                            role=MessageRole.ASSISTANT,
                            rating=Rating.POSITIVE,
                        ),
                    ],
                )
            }
        )

        await client.log.conversation_upsert(
            body={
                "conversation": Conversation(
                    messages=[
                        Message(
                            message="You are a helpful assistant!",
                            role=MessageRole.SYSTEM,
                        ),
                        Message(
                            message="Hello, world!",
                            role=MessageRole.USER,
                        ),
                        Message(
                            message="Hi, how can I help?",
                            role=MessageRole.ASSISTANT,
                            rating=Rating.POSITIVE,
                        ),
                    ],
                )
            }
        )


loop = asyncio.get_event_loop()
loop.run_until_complete(log())
loop.close()

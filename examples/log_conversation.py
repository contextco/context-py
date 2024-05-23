import getcontext
from getcontext.generated.models import Conversation, Message, MessageRole, Rating, Thread
from getcontext.token import Credential
import os

token = os.environ.get("GETCONTEXT_TOKEN")

c = getcontext.ContextAPI(credential=Credential(token))

c.log.conversation(
    body={
        "conversation": Conversation(
            feedback="The agent resolved my query very fast - thank you!",
            messages=[
                Message(
                    message="You are a helpful assistant!",
                    role=MessageRole.SYSTEM,
                    metadata={
                        "hi": "my_metadata",
                        }
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

c.log.conversation_thread(
    body={
        "conversation": Thread(
            id="Thread1234",
            messages=[
                Message(
                    message="You are a helpful assistant!",
                    role=MessageRole.SYSTEM,
                    metadata={
                        "hi": "my_metadata",
                        }
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

# Log against an API tenant.
c.log.conversation(
    tenant_id="1234",
    body={
        "conversation": Conversation(
            feedback="The agent resolved my query very fast - thank you!",
            messages=[
                Message(
                    message="You are a helpful assistant!",
                    role=MessageRole.SYSTEM,
                    metadata={
                        "hi": "my_metadata",
                        }
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

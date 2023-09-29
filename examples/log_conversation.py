import getcontext
from getcontext.generated.models import Conversation, Message, MessageRole, Rating
from getcontext.token import Credential
import os

token = os.environ.get("GETCONTEXT_TOKEN")

c = getcontext.ContextAPI(credential=Credential(token))

c.log.conversation(
    body={
        "conversation": Conversation(
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

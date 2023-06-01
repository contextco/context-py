# Context Python Library

[![PyPI version](https://badge.fury.io/py/context-python.svg)](https://badge.fury.io/py/context-python)

The Context Python library provides a convenient way to interface with the Context APIs. We include pre-defined classes and operations to interact with API resources.

## Installation

```
pip install --upgrade context-python
```

## Usage

The library needs to be configured with your Context API key, which is available in the [Context Settings Dashboard](https://go.getcontext.ai/settings).

### Synchronous Example

```python
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
```

### Async Example

```python
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


loop = asyncio.get_event_loop()
loop.run_until_complete(log())
loop.close()
```

## Appendix

```yaml
python: true
output-folder: getcontext/generated/
no-namespace-folders: true
credential-default-policy-type: BearerTokenCredentialPolicy
black: true
python3-only: true
add-credential: true
credential-scopes: all
models-mode: msrest
```

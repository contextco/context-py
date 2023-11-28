import getcontext
from getcontext.generated.models import TestCase, TestCaseMessage, TestSet, TestCaseFrom, TestCaseMessageRole
from getcontext.token import Credential
import os

token = os.environ.get("GETCONTEXT_TOKEN")

c = getcontext.ContextAPI(credential=Credential(token))

c.log.test_sets(
    copy_test_cases_from=TestCaseFrom.NONE,
    body=TestSet(
        name="Test Set 1",
        test_cases=[
            TestCase(
                name="Test Case 1",
                model="gpt-4",
                messages=[
                    TestCaseMessage(
                        message="You are a super LLM agent.",
                        role=TestCaseMessageRole.SYSTEM
                    ),
                    TestCaseMessage(
                        message="Tell me a story about Bob the cat.",
                        role=TestCaseMessageRole.USER
                    ),
                ]
            )
        ]
    )
)

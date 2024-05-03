import unittest
import os
import logging
import openai
from getcontext.tracing import (
    Trace,
    capture_trace,
    traceable,
    Evaluator,
    dynamic_traceable,
)
from langsmith.wrappers import wrap_openai
from getcontext.tracing.exceptions import EvaluationsFailedError


class TestTools(unittest.TestCase):
    @traceable
    def fib(n):
        a, b = 0, 1
        for _ in range(n):
            yield a
            a, b = b, a + b

    @traceable(run_type="chain")
    def fibonacci_dummy(a=5):
        return list(TestTools.fib(a))

    def setUp(self):
        # setup openai client with dynamic traceable
        self.openai_client = openai.Client()
        self.openai_client.chat.completions.create = dynamic_traceable(
            self.openai_client.chat.completions.create,
            run_type="llm",
            name="specific_name_openai_chat",
        )
        logging.basicConfig()
        logging.getLogger('context-ai').setLevel(logging.INFO)

    def test_in_normal_prod(self):
        # ensure functions are runnable normally without context.ai
        if "CONTEXT_DOMAIN" in os.environ:
            del os.environ["CONTEXT_DOMAIN"]
        TestTools.fibonacci_dummy

    def test_capture_trace_completes_function(self):
        TestTools.fibonacci_dummy(a=15)
        trace = capture_trace(TestTools.fibonacci_dummy, a=14, trace_name="my_trace")

        self.assertEqual(
            trace.result, [0, 1, 1, 2, 3, 5, 8, 13, 21, 34, 55, 89, 144, 233]
        )
        self.assertEqual(trace.run_tree.name, "my_trace")

    def test_capture_trace_raises_error_on_non_callable(self):
        with self.assertRaises(TypeError):
            capture_trace(5)

    def test_capture_trace_returns_trace_instance(self):
        trace = capture_trace(TestTools.fibonacci_dummy, 5)
        self.assertIsInstance(trace, Trace)

    def test_capture_trace_has_correct_parent_name(self):
        trace = capture_trace(TestTools.fibonacci_dummy)
        self.assertEqual(
            trace.run_tree.name, "test_capture_trace_has_correct_parent_name"
        )

    def test_capture_trace_has_correct_name(self):
        trace = capture_trace(TestTools.fibonacci_dummy, trace_name="brand_new_trace")
        self.assertEqual(trace.run_tree.name, "brand_new_trace")

    def test_capture_trace_returns_run_tree(self):
        trace = capture_trace(TestTools.fibonacci_dummy)
        self.assertIsNotNone(trace.run_tree)

    def test_trace_patch(self):
        trace = capture_trace(
            self.openai_client.chat.completions.create,
            messages=[
                {"role": "user", "content": "Tell me a fun fact about the world."}
            ],
            model="gpt-3.5-turbo",
        )

        golden_response_evaluator = Evaluator(
            evaluator="golden_response",
            options={
                "golden_response": "[0, 1, 1, 2, 3, 5, 8, 13, 21, 34]",
                "capitalization": "full",
                "punctuation": "full",
                "whitespace": "full",
            },
        )
        trace.add_evaluator("specific_name_openai_chat", golden_response_evaluator)

        self.assertEqual(
            trace.run_tree.child_runs[0].extra["context_ai_options"]["evaluators"][0],
            golden_response_evaluator,
        )

    def test_evaluator_llm(self):
        @traceable(run_type="chain")
        def openai_hello_world():
            return wrap_openai(openai.Client()).chat.completions.create(
                messages=[
                    {"role": "user", "content": "Tell me a fun fact about the world."}
                ],
                model="gpt-3.5-turbo",
            )

        trace = capture_trace(openai_hello_world)

        golden_response_evaluator = Evaluator(
            evaluator="golden_response",
            options={
                "golden_response": "Hello, world",
                "capitalization": "full",
                "punctuation": "full",
                "whitespace": "full",
            },
        )
        trace.add_evaluator("ChatOpenAI", golden_response_evaluator)

    ##############################
    # dynamic_traceable tests
    ##############################

    def my_multiplier(a=3):
        return 5 * a

    def test_dynamic_traceable_returns_function(self):
        dynamic_my_multiplier = dynamic_traceable(
            TestTools.my_multiplier, run_type="chain", name="my_multiplier"
        )

        self.assertEqual(dynamic_my_multiplier(), 15)
        self.assertEqual(dynamic_my_multiplier(5), 25)
        self.assertEqual(dynamic_my_multiplier(a=10), 50)

    def test_dynamic_traceable_has_correct_parent_name(self):
        dynamic_my_multiplier = dynamic_traceable(
            TestTools.my_multiplier, run_type="chain"
        )

        self.assertEqual(dynamic_my_multiplier.__name__, "my_multiplier")

    def test_dynamic_traceable_raises_error_on_non_callable(self):
        with self.assertRaises(TypeError):
            dynamic_traceable(5)

    def test_dynamic_traceable_with_capture_trace(self):
        dynamic_my_multiplier = dynamic_traceable(
            TestTools.my_multiplier, run_type="chain"
        )
        trace = capture_trace(dynamic_my_multiplier)

        self.assertEqual(trace.result, 15)

    def test_dynamic_traceable_with_capture_trace_openai(self):
        trace = capture_trace(
            self.openai_client.chat.completions.create,
            messages=[
                {"role": "user", "content": "Tell me a fun fact about the world."}
            ],
            model="gpt-3.5-turbo",
        )

        self.assertIsNotNone(trace.result)

    ##############################
    # trace evalution tests
    ##############################

    def test_trace_evaluate_pass(self):
        trace = capture_trace(
            self.openai_client.chat.completions.create,
            messages=[
                {"role": "user", "content": "Respond with exactly 'Hello, world'"}
            ],
            model="gpt-3.5-turbo",
        )
        trace.add_evaluator(
            span_name="specific_name_openai_chat",
            evaluator=Evaluator(
                evaluator="golden_response",
                options={"golden_response": "Hello, world"},
            ),
        )

        result = trace.evaluate()
        self.assertIsNotNone(result)

    def test_trace_evaluate_fail(self):
        trace = capture_trace(
            self.openai_client.chat.completions.create,
            messages=[
                {"role": "user", "content": "Respond with exactly 'Hello, world'"}
            ],
            model="gpt-3.5-turbo",
        )
        trace.add_evaluator(
            span_name="specific_name_openai_chat",
            evaluator=Evaluator(
                evaluator="golden_response",
                options={"golden_response": "Another random string!!!"},
            ),
        )

        with self.assertRaises(EvaluationsFailedError):
            trace.evaluate()

    def test_trace_multiple_test_cases(self):
        """Test that evaluators can be added to multiple spans in a trace"""

        @traceable(run_type="chain")
        def my_complex_llm_chain():
            client = openai.Client()

            joke_fetcher = dynamic_traceable(
                client.chat.completions.create,
                run_type="llm",
                name="joke_fetcher",
            )

            joke_fetcher(
                messages=[
                    {"role": "user", "content": "Tell me a fun fact about the world."}
                ],
                model="gpt-3.5-turbo",
            )

            serious_fact_fetcher = dynamic_traceable(
                client.chat.completions.create,
                run_type="llm",
                name="serious_fact_fetcher",
            )

            serious_fact_fetcher(
                messages=[
                    {
                        "role": "user",
                        "content": "Tell me a joke.",
                    }
                ],
                model="gpt-3.5-turbo",
            )

        trace = capture_trace(my_complex_llm_chain)

        trace.add_evaluator(
            span_name="joke_fetcher",
            evaluator=Evaluator(
                evaluator="attempts_answer",
            ),
        )
        trace.add_evaluator(
            span_name="serious_fact_fetcher",
            evaluator=Evaluator(
                evaluator="refuse_answer",
            ),
        )

    def test_trace_faithfulness(self):
        # NOTE: faithfulness is not working atm server side
        trace = capture_trace(
            self.openai_client.chat.completions.create,
            messages=[
                {"role": "system", "content": "The tallest building in the world is the Burj Khalifa."},
                {"role": "user", "content": "What is the name of the tallest building in the world?"},
            ],
            model="gpt-3.5-turbo",
        )
        trace.add_evaluator(
            span_name="specific_name_openai_chat",
            evaluator=Evaluator(
                evaluator="faithfulness",
            ),
        )
        trace.add_evaluator(
            span_name="specific_name_openai_chat",
            evaluator=Evaluator(
                evaluator="golden_response",
                options={"golden_response": "Burj Khalifa"},
            ),
        )

        with self.assertRaises(EvaluationsFailedError):
            trace.evaluate()

    ##############################
    # retriever tests
    ##############################

    @traceable
    def my_caller_func():
        from langchain_community.document_loaders import TextLoader
        from langchain_community.vectorstores import FAISS
        from langchain_openai import OpenAIEmbeddings
        from langchain_text_splitters import CharacterTextSplitter

        loader = TextLoader("./tests/state_of_the_union.txt")

        documents = loader.load()
        text_splitter = CharacterTextSplitter(chunk_size=1000, chunk_overlap=0)
        texts = text_splitter.split_documents(documents)
        embeddings = OpenAIEmbeddings()
        db = FAISS.from_documents(texts, embeddings)

        retriever = db.as_retriever()

        retriever.with_config({"run_name": "Custom run name"}).invoke("what did he say about ketanji brown jackson")

    def test_openai_retriever(self):
        capture_trace(TestTools.my_caller_func)


if __name__ == "__main__":
    unittest.main()

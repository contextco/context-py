import unittest
import os
import openai
from getcontext.tracing import Trace, capture_trace, traceable, Evaluator, wrap_openai, dynamic_traceable


class TestTools(unittest.TestCase):
    @traceable
    def fib(n):
        a, b = 0, 1
        for _ in range(n):
            yield a
            a, b = b, a + b
    
    @traceable(run_type='chain')
    def fibonacci_dummy(a=5):
        return list(TestTools.fib(a))
    
    def setUp(self):
        os.environ['CONTEXT_TRACE_ENDPOINT'] = 'http://api.localtest.me:3000/api/v1/evaluations/traces'
        os.environ['GETCONTEXT_TOKEN'] = 'TOKEN'

    def test_in_normal_prod(self):
        # ensure functions are runnable normally without context.ai
        if 'CONTEXT_TRACE_ENDPOINT' in os.environ:
            del os.environ['CONTEXT_TRACE_ENDPOINT']
        TestTools.fibonacci_dummy
    
    def test_capture_trace_completes_function(self):
        TestTools.fibonacci_dummy(a=15)
        trace = capture_trace(TestTools.fibonacci_dummy, a=14)
        
        self.assertEqual(trace.result, [0, 1, 1, 2, 3, 5, 8, 13, 21, 34, 55, 89, 144, 233])

    def test_capture_trace_raises_error_on_non_callable(self):
        with self.assertRaises(TypeError):
            capture_trace(5)
            
    def test_capture_trace_returns_trace_instance(self):
        trace = capture_trace(TestTools.fibonacci_dummy)
        self.assertIsInstance(trace, Trace)

    def test_capture_trace_has_correct_parent_name(self):
        trace = capture_trace(TestTools.fibonacci_dummy)
        self.assertEqual(trace.run_tree.name, 'test_capture_trace_has_correct_parent_name')
        
    def test_capture_trace_returns_run_tree(self):
        trace = capture_trace(TestTools.fibonacci_dummy)
        self.assertIsNotNone(trace.run_tree)
        
    def test_trace_patch(self):
        trace = capture_trace(TestTools.fibonacci_dummy)

        golden_response_evaluator = Evaluator(
            evaluator='golden_response',
            options={
                'golden_response': "[0, 1, 1, 2, 3, 5, 8, 13, 21, 34]",
                'capitalization': 'full',
                'punctuation': 'full',
                'whitespace': 'full'
                }
        )
        trace.add_evaluator('fibonacci_dummy', golden_response_evaluator)
        
        self.assertEqual(trace.run_tree.child_runs[0].extra['context_ai_options']['evaluators'][0], golden_response_evaluator)

    def test_evaluator_llm(self):
        @traceable(run_type='chain')
        def openai_hello_world():
            return wrap_openai(openai.Client()).chat.completions.create(
                messages=[{"role": "user", "content": "Tell me a fun fact about the world."}],
                model="gpt-3.5-turbo"
            )

        trace = capture_trace(openai_hello_world)

        golden_response_evaluator = Evaluator(
            evaluator='golden_response',
            options={
                'golden_response': 'Hello, world',
                'capitalization': 'full',
                'punctuation': 'full',
                'whitespace': 'full'
                }
        )
        trace.add_evaluator('ChatOpenAI', golden_response_evaluator)

    ##############################
    # dynamic_traceable tests
    ##############################

    def my_multiplier(a=3):
        return 5 * a

    def test_dynamic_traceable_returns_function(self):
        dynamic_my_multiplier = dynamic_traceable(TestTools.my_multiplier, run_type='chain', name='my_multiplier')

        self.assertEqual(dynamic_my_multiplier(), 15)
        self.assertEqual(dynamic_my_multiplier(5), 25)
        self.assertEqual(dynamic_my_multiplier(a=10), 50)

    def test_dynamic_traceable_has_correct_parent_name(self):
        dynamic_my_multiplier = dynamic_traceable(TestTools.my_multiplier, run_type='chain')

        self.assertEqual(dynamic_my_multiplier.__name__, 'my_multiplier')

    def test_dynamic_traceable_raises_error_on_non_callable(self):
        with self.assertRaises(TypeError):
            dynamic_traceable(5)

    def test_dynamic_traceable_with_capture_trace(self):
        dynamic_my_multiplier = dynamic_traceable(TestTools.my_multiplier, run_type='chain')
        trace = capture_trace(dynamic_my_multiplier)

        self.assertEqual(trace.result, 15)
        
    def test_dynamic_traceable_with_capture_trace_openai(self):
        openai_client = openai.Client()
        openai_client.chat.completions.create = dynamic_traceable(
            openai_client.chat.completions.create,
            run_type='llm',
            name='specific_name_openai_chat')

        trace = capture_trace(openai_client.chat.completions.create,
                              messages=[{"role": "user", "content": "Tell me a fun fact about the world."}],
                              model="gpt-3.5-turbo")

        self.assertIsNotNone(trace.result)


if __name__ == '__main__':
    unittest.main()

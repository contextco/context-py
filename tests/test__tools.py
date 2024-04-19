import unittest
from getcontext.tracing import Trace, capture_trace, traceable
import os


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
        os.environ['CONTEXT_SDK_DEV'] = 'true'
        os.environ['GETCONTEXT_TOKEN'] = 'TOKEN'

    def tearDown(self):
        del os.environ['CONTEXT_SDK_DEV']
    
    def test_capture_trace_completes_function(self):
        TestTools.fibonacci_dummy(a=15)
        trace = capture_trace(TestTools.fibonacci_dummy, a=14)
        
        trace.add_evaluator('fibonacci_dummy', {'smenatic_mathch': 'true'})
        
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
        # NOTE: getting exception from server
        trace = capture_trace(TestTools.fibonacci_dummy)
        # TODO: add correct evaluator details
        trace.add_evaluator('fibonacci_dummy', {'smenatic_mathch': 'true'})
        
        self.assertEqual(trace.run_tree.child_runs[0].extra['context_ai_options']['evaluators'][0], {'smenatic_mathch': 'true'})


if __name__ == '__main__':
    unittest.main()

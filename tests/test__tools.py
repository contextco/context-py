import unittest
from getcontext.tracing import Trace, capture_trace, traceable


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
    
    def test_capture_trace_completes_function(self):
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


if __name__ == '__main__':
    unittest.main()

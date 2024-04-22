import unittest
from getcontext.tracing import Trace, capture_trace, traceable


class RunTreeMock:
    def __init__(self, name):
        self.name = name
        self.child_runs = []
        self.extra = None
    
    def patch(self):
        pass


class TestTrace(unittest.TestCase):
    
    def test__find_run_no_run_tree(self):
        trace = Trace(1, None)
        with self.assertRaises(ValueError):
            trace._find_run('test')
            
    def test__find_run_no_matching_runs(self):
        trace = Trace(1, None)
        with self.assertRaises(ValueError):
            trace._find_run('test')
            
    def test__find_run_matching_runs_root(self):
        trace = Trace(1, RunTreeMock('test'))
        with self.assertRaises(ValueError):
            trace._find_run('test')
            
    def test__find_run_matching_runs_child(self):
        trace = Trace(1, RunTreeMock('root'))
        trace.run_tree.child_runs.append(RunTreeMock('test'))
        self.assertEqual(trace._find_run('test').name, 'test')
        
    def test__find_run_matching_runs_grandchild(self):
        trace = Trace(1, RunTreeMock('root'))
        trace.run_tree.child_runs.append(RunTreeMock('child'))
        trace.run_tree.child_runs[0].child_runs.append(RunTreeMock('test'))
        self.assertEqual(trace._find_run('test').name, 'test')
        
    def test__find_run_multiple_matching_runs(self):
        trace = Trace(1, RunTreeMock('root'))
        trace.run_tree.child_runs.append(RunTreeMock('test'))
        trace.run_tree.child_runs.append(RunTreeMock('test'))
        with self.assertRaises(ValueError):
            trace._find_run('test')
            
    def test_add_evaluator_cannot_add_to_unit_test_function(self):
        trace = Trace(1, RunTreeMock('test'))
        with self.assertRaises(ValueError):
            trace.add_evaluator('test', {})
    
    def test_add_evaluator(self):
        trace = Trace(1, RunTreeMock('root'))
        trace.run_tree.child_runs.append(RunTreeMock('child'))
        trace.add_evaluator('child', {'key': 'value'})
        self.assertEqual(trace.run_tree.child_runs[0].extra['context_ai_options']['evaluators'][0], {'key': 'value'})
        
    def test_add_evaluator_multiple_evaluators(self):
        trace = Trace(1, RunTreeMock('root'))
        trace.run_tree.child_runs.append(RunTreeMock('child'))
        trace.add_evaluator('child', {'key': 'value'})
        trace.add_evaluator('child', {'another_key': 'another_value'})
        self.assertEqual(len(trace.run_tree.child_runs[0].extra['context_ai_options']['evaluators']), 2)
        self.assertEqual(trace.run_tree.child_runs[0].extra['context_ai_options']['evaluators'][0], {'key': 'value'})
        self.assertEqual(trace.run_tree.child_runs[0].extra['context_ai_options']['evaluators'][1], {'another_key': 'another_value'})


if __name__ == '__main__':
    unittest.main()

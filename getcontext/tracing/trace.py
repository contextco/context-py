from langsmith.run_trees import RunTree


class Trace:
    # known key, which is interpreted on the server side
    CONTEXT_AI_OPTIONS = "context_ai_options"
    
    def __init__(self, result, run_tree: RunTree):
        self.result = result
        self.run_tree = run_tree
    
    # TODO: used typed stuff from sdk here
    def add_evaluator(self, span_name: str, evaluator: dict):        
        if span_name == self.run_tree.name:
            raise ValueError("Cannot add evaluator to unit test function.")

        langsmith_run = self._find_run(span_name)
        if langsmith_run.extra is None:
            langsmith_run.extra = {}
        context_ai_options = langsmith_run.extra.setdefault(Trace.CONTEXT_AI_OPTIONS, {})
        evaluators_options = context_ai_options.setdefault("evaluators", [])
        evaluators_options.append(evaluator)
        
        langsmith_run.patch()
        
    def _find_run(self, name: str) -> RunTree:
        if self.run_tree is None:
            raise ValueError("No run tree found.")
        
        matching_runs = self._find_run_helper(self.run_tree, name)
        
        if len(matching_runs) == 0:
            raise ValueError("No matching spans found.")
        elif len(matching_runs) > 1:
            raise ValueError("Multiple matching spans found. You must specify a unique span name.")
            
        return matching_runs[0]
        
    def _find_run_helper(self, run_tree: RunTree, name: str) -> RunTree:
        # recurssion is fine here beacuse we explicitly don't allow complicated deep trees server side
        matching_runs = []
        for run in run_tree.child_runs:
            if run.name == name:
                matching_runs.append(run)
            else:
                matching_runs += self._find_run_helper(run, name)
            
        return matching_runs

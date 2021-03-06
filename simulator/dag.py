from copy import deepcopy
from dataclasses import dataclass
from networkx import DiGraph, is_directed_acyclic_graph, topological_sort
from typing import List, Dict, Optional, Union


@dataclass
# TODO: If function logic starts getting complicated, then we should move this to a different file
class Function:
    """Class for defining a function, its required resources, execution time, etc."""
    unique_id: str                            # We need this to refer to individual functions in our DAG
    resources: Dict[str, Dict]                # Resources and accompanying information that this function can run on

# TODO: Maybe have dags contain functions
class Dag:
    """Class for describing DAGs of functions."""
    name: str
    functions: Dict[str, Function]
    slo: Optional[int]
    graph: DiGraph
    sealed: bool

    # TODO: SLOs are just defined as ints for now, need to figure out what they look like
    def __init__(self, _name: str, funs: List[Function]=[], _slo: Optional[int] = None):
        self.name = _name
        self.functions = {}
        self.slo = _slo
        self.graph = DiGraph()
        self.sealed = False
        for fun in funs:
            self.add_function(fun)

    def __contains__(self, index: str) -> bool:
        return index in self.functions

    def __getitem__(self, index: str) -> Function:
        return self.functions[index]

    def add_function(self, fun: Function):
        assert not self.sealed, "Tried to add function after DAG was sealed."
        assert fun.unique_id not in self.functions
        self.functions[fun.unique_id] = fun
        self.graph.add_node(fun.unique_id)

    def add_edge(self, fun1: Function, fun2: Function):
        assert not self.sealed, "Tried to add edge after DAG was sealed."
        if fun1.unique_id not in self.functions:
            self.add_function(fun1)
        if fun2.unique_id not in self.functions:
            self.add_function(fun2)
        self.graph.add_edge(fun1.unique_id, fun2.unique_id)

    def sanity_check(self):
        # Check that all nodes are present
        func_keys = set(self.functions.keys())
        graph_nodes = set(self.graph.nodes)
        assert func_keys == graph_nodes, "All functions must be present in the graph."
        # Check that there are no cycles
        assert is_directed_acyclic_graph(self.graph), "Function graph must actually be a DAG"

    def get_dep_graph_original(self) -> DiGraph:
        return self.graph

    def get_dep_graph_copy(self) -> DiGraph:
        return deepcopy(self.graph)

    # Haven't decided on the way we should interact with the execution order
    # The following method is one option
    def get_topological_execution_order(self) -> List[Function]:
        sorted_uids = topological_sort(self.graph)
        return list(map(lambda uid: self.functions[uid], sorted_uids))

    # The following methods are another
    def execute(self):
        self.sealed = True
        sorted_uids = topological_sort(self.graph)
        self._order = list(map(lambda uid: self.functions[uid], sorted_uids))
        self._pos = 0

    def next_function(self) -> Optional[Function]:
        if self.has_next_function():
            self._pos += 1
            return self._order[self._pos - 1]
        else:
            return None

    def has_next_function(self) -> bool:
        return self._pos < len(self._order)

    def peek_next_function(self) -> Optional[Function]:
        if self.has_next_function():
            return self._order[self._pos]
        else:
            return None





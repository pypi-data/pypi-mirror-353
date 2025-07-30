import numpy

class DecisionTreeClassifier:
    def __init__(self, max_depth: int = ..., min_samples_split: int = ..., min_samples_leaf: int = ..., type_function: int = ...) -> None:
        """__init__(self: example.DecisionTreeClassifier, max_depth: int = 1000000000, min_samples_split: int = 2, min_samples_leaf: int = 1, type_function: int = 1) -> None"""
    def build_tree(self, arg0: numpy.ndarray[numpy.longdouble], arg1: numpy.ndarray[numpy.int32]) -> None:
        """build_tree(self: example.DecisionTreeClassifier, arg0: numpy.ndarray[numpy.longdouble], arg1: numpy.ndarray[numpy.int32]) -> None"""
    def get_final_score(self) -> float:
        """get_final_score(self: example.DecisionTreeClassifier) -> float"""
    def predict_classes(self, arg0: numpy.ndarray[numpy.longdouble]) -> list[int]:
        """predict_classes(self: example.DecisionTreeClassifier, arg0: numpy.ndarray[numpy.longdouble]) -> list[int]"""
    def print(self) -> None:
        """print(self: example.DecisionTreeClassifier) -> None"""

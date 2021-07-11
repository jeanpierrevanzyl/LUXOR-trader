from abc import ABC, abstractmethod
import numpy as np

class WFA(ABC):

    def __init__(self, trader, optimization_window_size, unseen_window_size, window_increase_size=None):
        self.trader = trader
        self.optimization_window_size = optimization_window_size
        self.unseen_window_size = unseen_window_size
        self.window_increase_size = unseen_window_size if window_increase_size is None else window_increase_size
    
class aWFA(WFA):

    pass

class rWFA(WFA):

    pass

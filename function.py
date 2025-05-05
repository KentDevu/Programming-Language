from typing import List
from nodes import Node

class Function:
    def __init__(self, params: List[str], body: Node, is_method: bool = False):
        self.params = params
        self.body = body
        self.is_method = is_method
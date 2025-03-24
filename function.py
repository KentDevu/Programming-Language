from typing import List
from nodes import Node

class Function:
    def __init__(self, params: List[str], body: Node):
        self.params = params
        self.body = body
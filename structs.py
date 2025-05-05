from typing import List, Dict, Any
from function import Function

class StructDef:
    def __init__(self, fields: List[str], methods: Dict[str, Function] = None):
        self.fields = fields
        self.methods = methods or {}

class StructInstance:
    def __init__(self, struct_name: str, field_values: Dict[str, Any]):
        self.struct_name = struct_name
        self.fields = field_values
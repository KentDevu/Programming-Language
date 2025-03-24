from typing import List, Dict, Any

class StructDef:
    def __init__(self, fields: List[str]):
        self.fields = fields

class StructInstance:
    def __init__(self, struct_name: str, field_values: Dict[str, Any]):
        self.struct_name = struct_name
        self.fields = field_values
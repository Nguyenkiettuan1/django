import json
from uuid import UUID

class Obj():
    def is_empty(obj):
        if isinstance(obj, dict):
            return bool(obj)
        elif isinstance(obj, (list, tuple)):
            return len(obj) > 0
        else:
            return obj is not None
        
class Int():
    def is_int(value):
        try:
            int(value)
            return True
        except ValueError:
            return False   

class UUIDEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, UUID):
            # if the obj is uuid, we simply return the value of uuid
            return obj.hex
        return json.JSONEncoder.default(self, obj)
import json
from uuid import UUID
from django.forms.models import model_to_dict

class Obj():
    def is_empty(obj):
        if isinstance(obj, dict):
            return not bool(obj)
        elif isinstance(obj, (list, tuple)):
            return not len(obj) > 0
        else:
            return False
        
class Int():
    def is_int(value):
        try:
            int(value)
            return True
        except ValueError:
            return False   

class UUIDEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj):
            # if the obj is uuid, we simply return the value of uuid
            return obj.hex
        return json.JSONEncoder.default(self, obj)
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
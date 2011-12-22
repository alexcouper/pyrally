API_OBJECT_TYPES = {}


def register_type(class_type):
    global API_OBJECT_TYPES
    API_OBJECT_TYPES[class_type.rally_name] = class_type

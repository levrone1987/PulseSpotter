import importlib


def import_class(full_class_path):
    split_index = full_class_path.rfind(".")
    module_full_path = full_class_path[:split_index]
    class_name = full_class_path[split_index + 1:]
    module = importlib.import_module(module_full_path)
    cls = getattr(module, class_name)
    return cls

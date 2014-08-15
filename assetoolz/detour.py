import os


def detour_directory(path, func):
    for object_name in os.listdir(path):
        full_path = os.path.join(path, object_name)
        if os.path.isfile(full_path):
            func(full_path)
        elif os.path.isdir(full_path):
            detour_directory(full_path, func)

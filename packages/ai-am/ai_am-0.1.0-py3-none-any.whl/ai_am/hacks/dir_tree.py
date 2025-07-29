import os

def dirTree(path: str, indent: str = ""):
    """Prints the directory tree of the given path."""
    if not os.path.exists(path):
        print(f"Path '{path}' does not exist.")
        return

    for item in sorted(os.listdir(path)):
        full_path = os.path.join(path, item)
        print(indent + "├── " + item)
        if os.path.isdir(full_path):
            dirTree(full_path, indent + "│   ")

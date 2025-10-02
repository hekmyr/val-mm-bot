import sys

def log(message: str) -> None:
    print(message, flush=True)
    _ = sys.stdout.flush()

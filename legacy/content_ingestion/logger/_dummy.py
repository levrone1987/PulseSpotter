
class DummyLogger:
    def info(self, msg):
        print(f"INFO - {msg}")

    def debug(self, msg):
        print(f"DEBUG - {msg}")

    def warning(self, msg):
        print(f"WARNING - {msg}")

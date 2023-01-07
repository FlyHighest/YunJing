class ServerError(Exception):
    def __init__(self, *args: object) -> None:
        super().__init__(*args)

class NSFWDetected(Exception):
    def __init__(self, *args: object) -> None:
        super().__init__(*args)
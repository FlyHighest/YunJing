class ServerError(Exception):
    def __init__(self, *args: object) -> None:
        super().__init__(*args)

class NSFWDetected(Exception):
    def __init__(self, *args: object) -> None:
        super().__init__(*args)

class QueueTooLong(Exception):
    pass 

class TooFrequent(Exception):
    pass 

class NotLoginError(Exception):
    pass 

class ShareTooLow(Exception):
    pass 
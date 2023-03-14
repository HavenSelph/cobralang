class ReturnException(Exception):
    def __init__(self, value):
        self.value = value


class StopException(Exception):
    def __init__(self, code):
        self.code = code

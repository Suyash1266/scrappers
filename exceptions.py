class InvalidUrlError(ValueError):
    def __init__(self, message="Invalid URL format"):
        self.message = message
        super().__init__(message)
class ParseError(Exception):
    def __init__(
        self, message="An unexpected error occurred while parsing the output.Try Again"
    ):
        self.message = message
        super().__init__(self.message)



class NoValidDataError(Exception):
    """
    Exception for when the DataProfiler discovers there is no
    valid data
    """

    def __init__(self, message: str):
        """
        Constructor
        """
        super().__init__(message)
        self._message = message

    def get_message(self) -> str:
        """
        :return: The message from the expection
        """
        return self._message

class JerrisClientError(Exception):
    pass


class ResponseParsingExceptionValueTypeMismatch(JerrisClientError):
    pass


class ResponseParsingExceptionNullValue(JerrisClientError):
    pass

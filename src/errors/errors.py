"""
Errors of application.
"""


class InvalidFilePathError(FileNotFoundError):
    """
    This file path is invalid.
    """


class InvalidFileFormat(ValueError):
    """
    This file format is invalid.
    """


class CroppingError(ValueError):
    """
    Invalid image cropping coordinates
    """


class ReadFileError(ValueError):
    """
    Exception on file reading.
    """


class ValidationError(Exception):
    """
    Error what occurred via validation process.
    """
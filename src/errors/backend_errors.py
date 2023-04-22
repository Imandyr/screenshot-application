"""
Errors for application backend.
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
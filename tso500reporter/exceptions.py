"""
Exceptions
"""
from typing import List


class DuplicateKeyError(Exception):
    """
    Exception raised when duplicate keys are found during
    dict-flattening.

    Attributes:
        duplicate_keys: input salary which caused the error
    """

    def __init__(self, duplicate_keys: List) -> None:
        self.duplicate_keys = duplicate_keys
        self.message = "Duplicate keys found in input: {0}".format(
                ', '.join(duplicate_keys)
                )
        super().__init__(self.message)

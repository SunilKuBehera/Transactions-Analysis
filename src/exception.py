import sys
from src.logger import logging

def error_message_detail(error: Exception, error_detail: sys):
    """
    This function takes an exception and its details, and returns a formatted error message.
    """
    _, _, exc_tb = error_detail.exc_info()
    file_name = exc_tb.tb_frame.f_code.co_filename
    line_number = exc_tb.tb_lineno
    error_message = str(error)
    # Format the error message with file name, line number, and error message
    error_message = f"Error occurred in python script: [{file_name}] at line number: [{line_number}] with error message: [{error_message}]"
    return error_message

class CustomException(Exception):
    """
    Custom exception class that inherits from the built-in Exception class.
    It overrides the constructor to provide a detailed error message.
    """
    def __init__(self, error: Exception, error_detail: sys):
        super().__init__(error)
        self.error_message = error_message_detail(error, error_detail)

    def __str__(self):
        return self.error_message
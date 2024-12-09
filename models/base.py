import os
import sys
import traceback
from dataclasses import dataclass
from pathlib import Path


def is_relative_to(path1, path2):
    '''is_relative_to function for Python 3.6'''
    try:
        Path(path1).relative_to(path2)
        return True
    except ValueError:
        return False


@dataclass
class Error:
    '''Error Model'''
    title: str
    message: str

    @staticmethod
    def error_msg(err):
        error_class = err.__class__.__name__
        if len(err.args) > 0:
            detail = err.args[0]
        else:
            detail = ''
        _, _, tb = sys.exc_info()
        cwd = Path(os.getcwd())
        error_details = []
        for s in traceback.extract_tb(tb):
            slack_path = Path(s[0])
            line_number = s[1]
            module_name = s[2]
            if is_relative_to(slack_path, cwd):
                path_detail = slack_path.relative_to(cwd)
            else:
                path_detail = slack_path.name
            info = f'File \"{path_detail}\", line {line_number} in {module_name}'
            error_details.append(info)
        details = '\n'.join(error_details)
        err_msg = f'\n[{error_class}] {detail}'
        return f'\n{details}{err_msg}\n'

    @classmethod
    def from_exc(cls, exc_type_str: str, exc: Exception):
        return cls(title=exc_type_str,
                   message=Error.error_msg(exc))

import os
import platform

def locate_data_(file = None, stored_local=False):
    """Returns the directory where the data file is located."""

    current_wd = os.path.abspath(os.getcwd())
    if platform.system() == 'Windows':
        data_dir = '''\\data'''
        hash_slinging_slasher = '''\\'''
    else:
        data_dir = '''/data'''
        hash_slinging_slasher = '''/'''
    while not os.path.exists(current_wd + data_dir):
        if current_wd.rfind(hash_slinging_slasher) == -1:
            raise Exception('/data directory not found. Please store csv files in same folder as current file'
                            'and set value of stored_local back to True (default value with no input).')
        current_wd = current_wd[:current_wd.rfind(hash_slinging_slasher)]
    current_wd = current_wd + data_dir
    if stored_local:
        return os.path.abspath(os.getcwd())
    else:
        if file is not None:
            return current_wd + hash_slinging_slasher + file
        else:
            return current_wd

def correct_slash():
    """Returns the system specific correct slash"""
    if platform.system() == 'Windows':
        s = '''\\'''
    else:
        s = "/"
    return s 

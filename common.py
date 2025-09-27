import logging
import os
import datetime
from pathlib import Path


def when_modified(file_path: str) -> datetime.datetime | None:
    if not os.path.exists(file_path):
        logging.debug(f"Error! The file '{file_path}' not found.")
        return None
    mod_timestamp = os.path.getmtime(file_path)
    mod_datetime = datetime.datetime.fromtimestamp(mod_timestamp)
    logging.debug(f"The file '{file_path}' was last modified on: {mod_datetime}")
    return mod_datetime

def duration_calculator(dt_end:datetime.datetime = None, dt_srt:datetime.datetime = None) -> datetime.timedelta:
    dt_now = datetime.datetime.now()
    dt_end = dt_end if dt_end else dt_now
    dt_srt = dt_srt if dt_srt else dt_now
    return dt_end - dt_srt

def resolve_path(path_str: str) -> Path:
    expanded_vars = os.path.expandvars(path_str)
    expanded_user = Path(expanded_vars).expanduser()
    absolute_path = expanded_user.resolve()
    return absolute_path

def touch_file(filename: str):
    """
    Linux `touch` command
    """

    try:
        with open(filename, 'a'):
            os.utime(filename, None) 
    except OSError as e:
        logging.debug(f"Error touching file {filename}: {e}")

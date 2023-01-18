from pathlib import Path
import os
import logging

TOLERANCE = 10**-5


def resolve_ad_filepath(file_name: str, file_type: str) -> Path:
    """
    Given input filename, attempts to find the file, first by relative to cwd,
    then by absolute, the relative to ${AD_ROOT_DIR} enivironmental variable.
    If not found, prints error message indicating which file_type it is.
    """
    if Path(file_name).exists():
        return Path(file_name)
    elif Path(os.environ['AD_ROOT_DIR'], file_name).exists():
        return Path(os.environ['AD_ROOT_DIR'], file_name)

    msg = f'Could not find the {file_type} specified: {file_name}'
    logging.critical(msg)
    assert False, msg

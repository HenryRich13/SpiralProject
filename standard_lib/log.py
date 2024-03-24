from standard_lib.error import StandardError
import os
import datetime


class LogStatusType(object):
    INFO = 0
    SUCCESS = 1
    WARNING = 3
    ERROR = 4

    @classmethod
    def get_status(cls, status: int):
        if status == cls.INFO:
            return "INFO"
        if status == cls.SUCCESS:
            return "SUCCESS"
        if status == cls.WARNING:
            return "WARNING"
        if status == cls.ERROR:
            return "ERROR"


# <editor-fold desc="private vars">
__output_files = []
__min_quit_status: int = LogStatusType.ERROR
__time_format: str = "%m/%d/%Y %H:%M:%S:%f"
__format: str = f"<status WARNING\tmm/dd/YYYY HH:MM:SS:ffffff>\t"
__current_buffer = []
# </editor-fold>


def create_dir(path: str):
    parent = os.path.dirname(path)
    if parent != "" and not os.path.exists(parent):
        create_dir(parent)
    os.mkdir(path)


def create_log_file(folder: str, file_name: str, overwrite=False, append_file=True):
    if not os.path.exists(folder):
        create_dir(folder)
    full_path = os.path.join(folder, file_name)
    if not overwrite:
        open(full_path, "x").close()
    else:
        if os.path.exists(full_path):
            os.remove(full_path)
        open(full_path, "x").close()
    if append_file:
        __output_files.append(full_path)


def get_min_quit_status():
    return __min_quit_status


def set_min_quit_status(new_min_quit: int):
    global __min_quit_status
    __min_quit_status = new_min_quit


def get_time_format():
    return __time_format


def set_time_format(new_format: str):
    global __time_format
    __time_format = new_format


def put(*values: object, sep: str = " ", status: int = LogStatusType.INFO, files: str = None, flush_stream=True):
    current_time = datetime.datetime.now().strftime(__time_format)
    for f in files if files is not None else (None,) if len(__output_files) == 0 else __output_files:
        print(f"<status {LogStatusType.get_status(status)}\t{current_time}>\t"
              f"{f'{sep}'.join(str(val) for val in values)}", file=f, flush=flush_stream)
    if __min_quit_status is not None and __min_quit_status <= status:
        flush()
        raise StandardError("<standard_lib.log> min_quit_status reached. See output file for details")
    """<status WARNING  MM/DD/YYYY HH:MM:SS:ffffff> """


def buffer(*values: object, sep: str = " "):
    __current_buffer.append(sep.join(str(val) for val in values))


def clear():
    __current_buffer.clear()


def flush(end: str = "", sep: str = f"\n{''.join(' ' for _ in range(len(__format)))}",
          status=LogStatusType.INFO, files: str = None):
    if len(__current_buffer) == 0:
        return
    __current_buffer[-1] += end
    buf = tuple(__current_buffer)
    __current_buffer.clear()
    put(buf, sep=sep, status=status, files=files)

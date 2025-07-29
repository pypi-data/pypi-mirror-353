from enum import Enum
from typing import Dict, List, Coroutine
from io import BytesIO

import logging, zipfile, os, tarfile
import asyncio, threading, queue

KB = 1024
MB = KB * KB


class ImageFormatType(Enum):
    """Enum class type for Image Format Types

    Enum Options:
    - PIL_IMAGE = "pil_img"
    - BASE64_HTML_STRING = "base64_html_string"
    - NUMPY_ARRAY = "numpy_array"
    """
    PIL_IMAGE = "pil_img"
    BASE64_HTML_STRING = "base64_html_string"
    NUMPY_ARRAY = "numpy_array"


def get_custom_logger(name: str = "VirtS3", log_level: int = logging.INFO) -> logging.Logger:
    """Function to return a custom formatted logger object

    :param name: name of logger, defaults to 'VirtS3'
    :param log_level: desired logging level, defaults to logging.INFO
    :return: custom formatted Logger streaming to stdout
    """
    logger = logging.getLogger(name)
    logger.propagate = False
    
    # check if existing logger instance with same name exists
    if len(logger.handlers) > 0: return logger

    # check environment variable for DEBUG log level
    # else, default to INFO
    if os.getenv('VIRT_S3_DEBUG') and os.getenv('VIRT_S3_DEBUG').strip() == "1":
        log_level = logging.DEBUG

    # handlers
    stream_handler = logging.StreamHandler()
    stream_handler.setLevel(log_level)

    # formatters
    formatter = logging.Formatter(f'[%(name)s][%(asctime)s][%(filename)s][%(levelname)s]: %(message)s', "%Y-%m-%d %H:%M:%S %Z")
    stream_handler.setFormatter(formatter)
    logger.setLevel(log_level)
    logger.handlers = [stream_handler]
    return logger



logger = get_custom_logger()


def archive_zip_as_buffer(data_bytes_dict: Dict[str, bytes]) -> BytesIO:
    """Function to create a zip archive from dictionary of expected archive filepaths
    and data bytes
    
    :param data_bytes_dict: { "/path/to/data/file/in/archive/file.extension": data_as_bytes_obj }
    :return: zipped buffer BytesIO object
    """
    zip_buffer = BytesIO()
    with zipfile.ZipFile(zip_buffer, "a", zipfile.ZIP_DEFLATED, False) as z:
        for fpath, data_bytes in data_bytes_dict.items():
            z.writestr(fpath, data_bytes)
    
    zip_buffer.seek(0)

    return zip_buffer


def archive_tar_as_buffer(
    data_bytes_dict: Dict[str, bytes],
    compress: bool = False
) -> BytesIO:
    """Function to create a tar or tar.gz archive from a dictionary of expected archive filepaths

    :param data_bytes_dict: { "path/in/archive/file.ext": data_as_bytes }
    :param compress: flag to compress archive tar as .tar.gz - if not specified, uses .tar, defaults to False
    :return: BytesIO object containing the archive
    """
    mode = 'w:gz' if compress else 'w'
    tar_buffer = BytesIO()

    with tarfile.open(fileobj=tar_buffer, mode=mode) as tar:
        for arcname, data_bytes in data_bytes_dict.items():
            info = tarfile.TarInfo(name=arcname)
            info.size = len(data_bytes)
            tar.addfile(tarinfo=info, fileobj=BytesIO(data_bytes))

    tar_buffer.seek(0)
    
    return tar_buffer


def extract_archive_file(
    fpath: str, 
    extract_to: str, 
    seen_archives: Dict[str, int] = {},
    remove_extra_metadata: bool = True
) -> str:
    """Recursive function to extract contents of an archived file recursively
    
    Supports the following archive file extensions:
    * `.zip`
    * `.tar`
    * `.tar.gz`

    :param fpath: path to local archive file
    :param extract_to: path to directory to extract archive file
    :param seen_archives: dictionary of seen archive file paths that have already been extracted, defaults to {}
    :param remove_extra_metadata: bool flag to remove the extra `._*` files that result from MACOS, defaults to True
    :return: string path to extract_to directory
    """
    read_mode = None
    is_tar = False
    is_zip = False
    if fpath.endswith(".tar.gz"):
        read_mode = "r:gz"
        is_tar = True
    elif fpath.endswith(".tar"):
        read_mode = "r:"
        is_tar = True
    elif fpath.endswith(".zip"):
        read_mode = "r"
        is_zip = True
    
    if read_mode is None:
        raise ValueError(f"Expected file path to end in '.tar', '.tar.gz', or '.zip` file extension")
    
    if is_zip:
        # extract the zip file
        with zipfile.ZipFile(fpath, read_mode) as zip_ref:
            zip_ref.extractall(extract_to)

    elif is_tar: 
        # extract tar file
        with tarfile.open(fpath, read_mode) as tar:
            tar.extractall(path=extract_to)
            logger.info(f"Extracted to: {extract_to}")

    # walk through extracted files to find nested archive files
    for root, dirs, files in os.walk(extract_to):
        for file in files:
            fpath = os.path.join(root, file)
            
            # check if unseen nested zip
            if file.endswith('.zip') or file.endswith(".tar") or file.endswith(".tar.gz"):
                if fpath not in seen_archives:
                    # track seen archive files
                    seen_archives[fpath] = 1
                    nested_archive_fpath = fpath

                    # recursive call
                    logger.info(f"Extracting nested archive: {nested_archive_fpath}")
                    extract_archive_file(nested_archive_fpath, root, seen_archives=seen_archives)

                    # remove the zip file after extraction
                    os.remove(nested_archive_fpath)
    
    # remove extra metadata files
    if remove_extra_metadata:
        for root, dirs, files in os.walk(extract_to):
            for file in files:
                fpath = os.path.join(root, file)
                if file.startswith("._"):
                    os.remove(fpath)
                    continue
                logger.debug(f"Extracting: {fpath}")

    
    return extract_to


def format_bytes(num_bytes: int) -> str:
    """Funtion to take as input a number of bytes 
    and return a formatted string for B, KB, MB, GB
    rounded to 2 decimal places

    :param num_bytes: integer number of bytes
    :return: formatted byte string (e.g 5.11 MB )
    """
    # Define the units in increasing size order
    units = ["B", "KB", "MB", "GB", "TB"]
    
    # Start with bytes, and progressively divide by 1024 for each next unit
    unit_index = 0
    while num_bytes >= 1024 and unit_index < len(units) - 1:
        num_bytes /= 1024
        unit_index += 1

    # Format the number to 2 decimal places and return the formatted string
    return f"{num_bytes:.2f} {units[unit_index]}"


def run_async_func_in_new_event_loop_in_thread(partial_func: callable) -> any:
    """Synchronous function to run an async function in a new event loop thread.

    :param partial_func: partial function to call
    """
    def run(res_queue: queue.Queue):
        logger.debug(f"Thread {threading.current_thread().name} started.")
        res = None
        try:
            # Create a new event loop
            new_loop = asyncio.new_event_loop()
            # Set the newly created event loop as the current loop in this thread
            asyncio.set_event_loop(new_loop)
            # Run some asyncio code in the new loop
            res = new_loop.run_until_complete(partial_func())
        except Exception as e:
            logger.error(f"ErrorRunningAsyncFunction: {e}")
            raise e
        finally:
            new_loop.close()
            # add result to result queue
            res_queue.put(res)
            logger.debug(f"Thread {threading.current_thread().name} finished.")

    # Start a new thread that will create and use its own event 
    logger.debug("Main event loop starting...")
    # create result queue
    res_queue = queue.Queue()
    # initialize thread
    thread = threading.Thread(target=run, args=(res_queue,))
    # start thread
    thread.start()
    # Wait for the thread to finish
    thread.join() 
    logger.debug("Main event loop finished.")
    # return queue result
    return res_queue.get()


async def run_concurrent_tasks(tasks: List[Coroutine]) -> List[any]:
    """Async function to run list of coroutines (concurrently).
    Results are preserved in same order as input tasks.

    :param tasks: list of async coroutines
    :return: list of results from each coroutine. Results are preserved in same order as input tasks.
    """
    return await asyncio.gather(*tasks)

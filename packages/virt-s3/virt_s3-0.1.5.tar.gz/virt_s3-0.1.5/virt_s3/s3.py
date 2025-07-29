from virt_s3.utils import (
    get_custom_logger, 
    ImageFormatType, 
    archive_zip_as_buffer, 
    MB,
    extract_archive_file
)
from concurrent.futures import ThreadPoolExecutor
from io import BytesIO
from dataclasses import dataclass as pydataclass
from typing import List, Generator, Union, Any, Optional, Callable, Dict
from urllib.parse import urlparse
import os, zipfile, base64, time, traceback, threading, pathlib, shutil, functools

logger = get_custom_logger()

threading_lock = threading.Lock()

# Predict backend
try: 
    from predict_backend.store.connection_store import connection_store
except ModuleNotFoundError as me: 
    logger.warning(f"{me} -> Install 'predict-backend' to use the ConnectionStore")
    connection_store = None

# Boto3
try:
    from boto3 import Session
    from boto3.s3.transfer import TransferConfig
    from botocore.exceptions import ClientError
except ModuleNotFoundError as me:
    logger.warning(f"{me} -> `$ poetry install -E s3` to use.")
    class Session: 
        pass
    class TransferConfig: 
        def __init__(self, max_concurrency: int = 3):
            pass
    class ClientError(Exception):
        def __init__(self, *args):
            super().__init__(*args)


# Numpy and Pillow
try: 
    from PIL import Image
except ModuleNotFoundError as me:
    class Image:
        class Image: 
            pass
    logger.warning(f"{me} -> `$ poetry install -E image` to use.")

try: 
    import numpy as np
except ModuleNotFoundError as me:
    class np:
        class ndarray:
            pass
    logger.warning(f"{me} -> `$ poetry install -E image` to use.")


@pydataclass
class PredictConnectionStoreParams:
    """Dataclass for Predict Connection Store Parameters

    :param user_id: predict user id
    :param store_name: connection store name
    :param store_owner: connection store owner
    """
    user_id: str
    store_name: str
    store_owner: str

@pydataclass
class S3Params:
    """Dataclass for S3 Boto3 Connection Parameters

    Required:
    - `bucket_name`
    - `endpoint_url`

    Optional:
    - `region_name`

    Authentication Methods (and necessary params):

    1. Explicit Credentials
        - `aws_access_key_id`
        - `aws_secret_access_key`

    2. AWS Profile
        - `profile_name`

    3. Predict Backend Connection Store
        - `connection_store_params`

    :param bucket_name: aws s3 bucket
    :param endpoint_url: aws s3 url
    :param aws_access_key_id: your aws access key id, defaults to None
    :param aws_secret_access_key: your aws secret access key, defaults to None
    :param region_name: your aws region name, defaults to None
    :param profile_name: your aws IAM profile name, defaults to None
    :param connection_store_params: instance of PredictConnectionStoreParams, defaults to None
    """
    # AWS
    bucket_name: str
    endpoint_url: str
    aws_access_key_id: str = None
    aws_secret_access_key: str = None
    region_name: str = None
    profile_name: str = None
    # Predict
    connection_store_params: PredictConnectionStoreParams = None


class S3SessionManager:
    """Session Context Manager for S3

    :param s3_params: instance of S3Params, defaults to None
    :param s3_client: boto3 s3 client object, defaults to None
    :param keep_open: boolean flag to keep the session open or not outside of the context manager scope, defaults to False
    """
    def __init__(
        self,
        s3_params: S3Params = None,
        s3_client: Session = None,
        keep_open: bool = False,
        **session_client_kwargs
    ) -> None:

        # use default if not provided
        if s3_params is None and s3_client is None: 
            s3_params = get_s3_default_params()
        self.s3_params = s3_params
        self.s3_client = s3_client
        self.kwargs = session_client_kwargs
        self.keep_open = keep_open
        self.status = None

    def __enter__(self): 
        # create session client if not provided
        if self.s3_client is None: 
            self.s3_client = get_s3_session_client(self.s3_params, **self.kwargs)
        self.status = "open"
        return self.s3_client

    def __exit__(self, exc_type, exc_value, exc_tb):
        if self.s3_client and self.keep_open is False:
            self.s3_client.close()
            self.status = "closed"
        
        if exc_value or exc_type or exc_tb:
            fmt_tb = ''.join(traceback.format_exception(exc_type, exc_value, exc_tb))
            logger.error(f"S3SessionManagerError! (See Below)\n{fmt_tb}")
            return False


# Valid S3 Session and Client Args
VALID_S3_SESSION_ARGS = {
    'aws_access_key_id',
    'aws_secret_access_key',
    'aws_session_token',
    'region_name',
    'botocore_session',
    'profile_name'
}
VALID_S3_CLIENT_ARGS = {
    'region_name',
    'api_version',
    'use_ssl',
    'verify',
    'endpoint_url',
    'aws_access_key_id',
    'aws_secret_access_key',
    'aws_session_token',
    'config'
}


## Manage in-memory record of which function is fastest for upload and download over time
# calculating megabytes per second
# Download: get_s3_file_simple() or get_s3_file_transfer()
# Upload: upload_to_s3_simple() or upload_to_s3_transfer()

MAX_UPLOAD_DOWNLOAD_COUNT = 10

@pydataclass
class PerformanceMetrics:
    """Dataclass for different performance metrics

    :param mbps: megabytes per second, defaults to 0.0
    """
    mbps: float = 0.0

class PerformanceRecord:
    """Encpasulates performance for a given performance monitoring type

    :param _type: 'upload' or 'download'
    :param metrics: dictionary of function name str -> list of PerformanceMetrics, defaults to { 'simple': [], 'transfer': [] }
    :param count: number of times this performance record has been updated, defaults to 0
    :param chosen_func: the specific function key name that was chosen to be run, defaults to None
    """
    def __init__(
        self,
        _type: str,
        metrics: Dict[str, List[PerformanceMetrics]] = {
            'simple': [],
            'transfer': []
        },
        count: int = 0,
        chosen_func: str = None
    ) -> None:
        self._type = _type
        self.metrics = metrics
        self.count = count
        self.chosen_func = chosen_func
   

class UploadDownloadPerformanceManager:
    """Class used to record and determine which different upload or download
    function to run based on a record of performance metrics over the course of
    the program run lifetime
    """
    def __init__(self) -> None:
        self.records_dict = {
            'upload': PerformanceRecord('upload'),
            'download': PerformanceRecord('download')
        }

    def reset(self, _type: str):
        """Method to reset the performance records dictionary

        :param _type: 'upload' or 'download'
        """
        self.records_dict[_type].metrics['simple'] = []
        self.records_dict[_type].metrics['transfer'] = []
        self.records_dict[_type].count = 0

    def average_metrics(self, metrics_li: List[PerformanceMetrics]) -> PerformanceMetrics:
        """Method to get average of list of metrics

        :param metrics_li: list of PerformanceMetrics
        :return: single instance of PerformanceMetrics aggregated as simple average
        """
        n, total = len(metrics_li), 0.0
        if n < 1: return PerformanceMetrics(mbps=0.0)
        for metric in metrics_li: total += metric.mbps
        avg = total / n
        return PerformanceMetrics(mbps=round(avg, 2))

    def get_metrics(self, _type: str, func_str: str) -> List[PerformanceMetrics]:
        """Method to get the specific function PerformanceMetrics

        :param _type: 'upload' or 'download'
        :param func_str: name of function key that you want to return list of PerformanceMetrics for
        :return: list of PerformanceMetrics
        """
        return self.records_dict[_type].metrics[func_str]

    def override_chosen_func(self, _type: str, override_choice: str = "transfer") -> None:
        """Method to override the perviously chosen function

        :param _type: 'upload' or 'download'
       :param override_choice: 'transfer' or 'simple', defaults to 'transfer'
        """
        # set chosen func
        self.records_dict[_type].chosen_func = override_choice
        return
        
    def choose_function(self, _type: str) -> str:
        """Method to choose the right function to run based on historical throughput MBPS

        :param _type: 'upload' or 'download'
        :return: chosen function string name
        """
        # determine which function to use for download
        perf_record = self.records_dict[_type]
        simple_mbps = self.average_metrics(perf_record.metrics['simple']).mbps
        transfer_mbps = self.average_metrics(perf_record.metrics['transfer']).mbps
        
        # default to 'transfer' option
        chosen_func = "transfer"
        # both no history, use transfer
        if simple_mbps == 0 and transfer_mbps == 0: chosen_func = "transfer"
        # simple has no history, but transfer has history
        elif simple_mbps == 0 and transfer_mbps > 0: chosen_func = "simple"
        # simple has history, but transfer has no history
        elif simple_mbps > 0 and transfer_mbps == 0: chosen_func = "transfer"
        # both have history -- calculate megabytes per second and compare
        elif simple_mbps > 0 and transfer_mbps > 0:
            chosen_func = "simple"
            # compare head to head
            if transfer_mbps > simple_mbps:
                chosen_func = "transfer"
            # Every N calls, reset things
            if perf_record.count >= MAX_UPLOAD_DOWNLOAD_COUNT: 
                logger.debug(f"Shaking Things up! Resetting UploadDownloadPerformanceManager")
                self.reset(_type)

        # set chosen func
        self.records_dict[_type].chosen_func = chosen_func
        return chosen_func
    
    def update_performance_record(
        self, 
        _type: str, 
        bytes_transferred: int, 
        transfer_time: float
    ) -> None:
        """Method used to update the performance record based
        with throughput metrics

        :param _type: 'upload' or 'download'
        :param bytes_transferred: number of bytes transferred
        :param transfer_time: total seconds the transfer took
        """
        mbps = round((bytes_transferred / MB) / transfer_time, 2)
        chosen_func = self.records_dict[_type].chosen_func
        self.records_dict[_type].metrics[chosen_func].append(PerformanceMetrics(mbps=mbps))
        self.records_dict[_type].count += 1

###################################################
########### GLOBAL PERFORMANCE MANGER #############
###################################################

performance_manager = UploadDownloadPerformanceManager()

###################################################
################ AWS S3 Functions #################
###################################################


def manage_s3_session(func):
    """Decorator function to manage s3 client session for functions that rely on virt-s3

    Expectations:
    - `s3_params` and `s3_client` are kwargs of the function

    :param func: function to wrap decorator with to use virt-s3 functionality
    """
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        try:
            # default checkers to False
            s3_params_passed_in = False
            s3_client_passed_in = False

            # get s3_params and s3_clients from func kwargs
            # if either not found, then this will result in an error
            s3_params = kwargs.get('s3_params')
            s3_client = kwargs.get('s3_client')

            # if passed in set variables to True
            if s3_params is not None: s3_params_passed_in = True
            if s3_client is not None: s3_client_passed_in = True

            # if params not passed in create new instance of default params
            # and add into kwargs
            if not s3_params_passed_in:
                s3_params = get_s3_default_params()
                kwargs['s3_params'] = s3_params

            # if client is passed in, go ahead and just run function as-is
            # no need to open a new session
            if s3_client_passed_in:
                return func(*args, **kwargs)
            
            # if client is not passed in, we shoud go ahead and create a new session
            # and pass in the client via kwargs
            logger.debug(f"[@manage_s3_session] Automatically OPENING S3 Session")
            with S3SessionManager(params=s3_params) as s3_client:
                kwargs['s3_client'] = s3_client
                res = func(*args, **kwargs)

            logger.debug(f"[@manage_s3_session] Automatically CLOSING S3 Session")
            # return function result
            return res

        except Exception as e:
            func_name = func.__name__
            new_msg = f"[@manage_s3_session] Caught Exception in {func_name}{args} -> {repr(e)}"
            logger.warning(new_msg)
            raise

    return wrapper


def get_s3_default_params() -> S3Params:
    """Function to get kwargs necessary for S3 connections

    :return: instance of S3Params
    """
    # get necessary environment variables
    s3_url = os.environ.get("S3_URL")
    s3_default_bucket = os.environ.get("S3_DEFAULT_BUCKET", "default-bucket")
    aws_secret_access_key = os.environ.get("AWS_SECRET_ACCESS_KEY")
    aws_access_key_id = os.environ.get("AWS_ACCESS_KEY_ID")
    aws_region = os.environ.get("AWS_REGION")

    kwargs = {
        'bucket_name': s3_default_bucket,
        'endpoint_url': s3_url,
        'region_name': aws_region
    }
    use_access_key = aws_access_key_id is not None and aws_secret_access_key is not None
    if use_access_key:
        access_kwargs = {
            'aws_access_key_id': aws_access_key_id,
            'aws_secret_access_key': aws_secret_access_key
        }
        kwargs = dict(**access_kwargs, **kwargs)
    
    return S3Params(**kwargs)


def get_s3_session_client(s3_params: S3Params, **kwargs) -> Session:
    """Function to get an S3 Boto3 Session client

    Authentication priority in case multiple options are provided:
    1. explicit supplied credentials (aws_access_key_id, aws_secret_access_key)
    2. aws profile
    3. connection store

    :param s3_params: instance of S3Params outlining s3 connectin parameters
    :return: instance of boto3.Session.client that can be used to make requests to S3
    """
    logger.debug(f"Getting S3 Session Client")
    # Format S3 Session Client Args
    s3_args = kwargs

    if s3_params.aws_access_key_id:
        s3_args = {
            "aws_access_key_id": s3_params.aws_access_key_id,
            "aws_secret_access_key": s3_params.aws_secret_access_key,
            **kwargs
        }

    elif s3_params.connection_store_params and connection_store:
        s3_args = {
            **connection_store.get_connection(
                name=s3_params.connection_store_params.store_name,
                connection_owner=s3_params.connection_store_params.store_owner,
                user_id=s3_params.connection_store_params.user_id,
            ),
            **kwargs
        }
    elif s3_params.profile_name:
        s3_args = {
            "profile_name": s3_params.profile_name,
            **kwargs
        }

    # Add S3 URL to all configurations
    if s3_params.endpoint_url:
        s3_args['endpoint_url'] = s3_params.endpoint_url

    session_args = {k: v for k, v in s3_args.items() if k in VALID_S3_SESSION_ARGS}
    client_args = {k: v for k, v in s3_args.items() if k in VALID_S3_CLIENT_ARGS}

    # Get session client
    # config = Config(read_timeout=300, connect_timeout=300, retries={"max_attempts": 3})
    return Session(**session_args).client('s3', **client_args)


@manage_s3_session
def create_s3_bucket(
    bucket_name: str, 
    s3_client = None,
    s3_params: S3Params = None,
    **kwargs
) -> bool:
    """Function to create an S3 Bucket

    :param bucket_name: name of bucket to create
    :param s3_client: boto3 s3 client object, defaults to None
    :param s3_params: instance of S3Params, defaults to None
    :param local_fs_params: instance of LocalFSParams, defaults to None
    :return: True if successfully created, else False
    """
    logger.info(f"Creating S3 bucket: {bucket_name}")

    # S3 kwargs (defaults are empty, but can be passed in)
    create_args = { "Bucket": bucket_name }
    bucket_encryption_args = {}
    block_bucket_public_access_args = {}
    bucket_policy_args = {}

    # defaults vs passed in
    create_args = kwargs.get('create_args', create_args)
    bucket_encryption_args = kwargs.get('bucket_encryption_args', bucket_encryption_args)
    block_bucket_public_access_args = kwargs.get('block_bucket_public_access_args', block_bucket_public_access_args)
    bucket_policy_args = kwargs.get('bucket_policy_args', bucket_policy_args)
    
    if s3_params.region_name and s3_params.region_name != 'us-east-1':
        create_args['CreateBucketConfiguration'] = {'LocationConstraint': s3_params.region_name}
    try:
        response = s3_client.create_bucket(**create_args)
        logger.info(f'response: {response}')
        logger.info(f'Bucket: {bucket_name} created in {s3_params.region_name}')
    except (s3_client.exceptions.BucketAlreadyExists, s3_client.exceptions.BucketAlreadyOwnedByYou) as e:
        logger.info(f'bucket: {bucket_name} already exists: {e}')
        return True
    except Exception as e:
        logger.error(f'Unhandled Exception in S3Handler.create_bucket: {e}')
        return False
    try:
        if len(bucket_encryption_args) > 0:
            s3_client.put_bucket_encryption(**bucket_encryption_args)
            logger.info(f'Bucket encryption enabled')
        if len(block_bucket_public_access_args) > 0:
            s3_client.put_public_access_block(**block_bucket_public_access_args)
            logger.info(f'Bucket public access blocked')
        if len(bucket_policy_args) > 0:
            s3_client.put_bucket_policy(**bucket_policy_args)
            logger.info(f'Bucket access policy set')
    except Exception as e:
        logger.error(f'Unhandled Exception in S3Handler setting policies: {e}')
    return True


@manage_s3_session
def get_s3_file_chunked(
    s3_fpath: str, 
    s3_client = None,
    s3_params: S3Params = None,
    chunk_size: int = 1 * MB,
    progress_callback: Callable[[int, int], any] = None,
    bytes_io: bool = False,
    **kwargs
) -> Union[BytesIO, bytes, None]: 
    """Function to read an s3 file using a chunking loop. This can be useful
    when trying to get very large files (relies on boto3.s3.get_object())

    :param s3_fpath: s3 key
    :param s3_client: boto3 s3 client object, defaults to None
    :param s3_params: instance of S3Params, defaults to None
    :param chunk_size: integer number of bytes per chunk to download, defaults to 1 * MB
    :param progress_callback: user-defined custom progress callback that is called throughout the download process that takes as input \
        (current number of bytes downloaded so far, total number of bytes to download)
    :param bytes_io: flag to convert pulled object as BytesIO instance, defaults to False
    :return: either BytesIO object, bytes object, or None
    """
    logger.info(f"get_s3_file_chunked(): {s3_fpath}")
    # get size of object to read in
    object_size = s3_client.get_object_attributes(
        Bucket=s3_params.bucket_name, 
        Key=s3_fpath, 
        ObjectAttributes=["ObjectSize"]
    ).get("ObjectSize")

    # chunking parameters
    # 100 MB
    chunk_start = 0
    chunk_end = chunk_start + chunk_size - 1

    # handle progress callback
    curr_transferred = 0
    def _custom_progress_callback(chunk_length: int):
        nonlocal curr_transferred
        nonlocal object_size
        curr_transferred += chunk_length
        # call passed in progress callback function
        progress_callback(curr_transferred, object_size)

    # resulting buffer to write to
    buffer = BytesIO()

    while chunk_start <= object_size:
        body = s3_client.get_object(
            Bucket=s3_params.bucket_name, 
            Key=s3_fpath, 
            Range=f"bytes={chunk_start}-{chunk_end}"
        ).get("Body")

        # if returned body is None, don't process
        if not body: continue

        # read in chunk bytes
        chunk = body.read()
        
        # write  chunk to buffer
        buffer.write(chunk)

        # progress callback
        if progress_callback: _custom_progress_callback(chunk_end-chunk_start)
        
        # move iteration forward
        chunk_start += chunk_size
        chunk_end += chunk_size
    
    # seek buffer to start
    buffer.seek(0)

    # return None if empty buffer
    if buffer.getbuffer().nbytes < 1: 
        return None
    
    # bytesio
    if bytes_io: return buffer
    # bytes
    return buffer.getvalue()


@manage_s3_session
def get_s3_file_simple(
    s3_fpath: str, 
    s3_client = None,
    s3_params: S3Params = None,
    bytes_io: bool = False,
    **kwargs
) -> Union[BytesIO, bytes, None]:
    """Function to downlad a given s3 file (relies on boto3.s3.get_object())

    :param s3_fpath: key to s3 file to download
    :param s3_client: provided s3 client object, defaults to None
    :param s3_params: provided instance of S3Params, defaults to None
    :param bytes_io: flag to convert pulled object as BytesIO instance, defaults to False
    :return: either bytes object, BytesIO object, or None
    """
    logger.info(f"get_s3_file_simple(): {s3_fpath}")
    try:
        resp = s3_client.get_object(Bucket=s3_params.bucket_name, Key=s3_fpath)
    except ClientError as ce:
        logger.warning(f"Failed to get S3 object: {s3_fpath}")
        return None
    
    # Only continue processing if HTTP 200 Status Code in Repsonse
    if resp.get('ResponseMetadata', {}).get('HTTPStatusCode', 400) != 200: return None
    
    obj = resp['Body']
    
    # Try reading data all at once
    object_data = obj.read()
    # bytes
    if not bytes_io: return object_data
    # BytesIO
    object_data = BytesIO(object_data)
    object_data.seek(0)
    return object_data


@manage_s3_session
def get_s3_file_transfer(
    s3_fpath: str, 
    s3_client = None,
    s3_params: S3Params = None,
    progress_callback: Callable[[int, int], any] = None,
    transfer_config: TransferConfig = TransferConfig(max_concurrency=3),
    bytes_io: bool = False,
    **kwargs
) -> Union[BytesIO, bytes, None]:
    """Function to downlad a given s3 file (relies on boto3.s3.download_fileobj())

    :param s3_fpath: key to s3 file to download
    :param s3_client: provided s3 client object, defaults to None
    :param s3_params: provided instance of S3Params, defaults to None
    :param progress_callback: user-defined custom progress callback that is called throughout the download process that takes as input \
        (current number of bytes downloaded so far, total number of bytes to download)
    :param transfer_config: instance of \
        [boto3.s3.transfer.TransferConfig](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/customizations/s3.html#boto3.s3.transfer.TransferConfig),\
        defaults to boto3.s3.transfer.TransferConfig(max_concurrency=3)
    :param bytes_io: flag to convert pulled object as BytesIO instance, defaults to False
    :return: either bytes object, BytesIO object, or None
    """
    logger.info(f"get_s3_file_transfer(): {s3_fpath}")
    # handle progress callback
    callback = None
    if progress_callback:        
        try:
            # get size of object to read in
            object_size = s3_client.get_object_attributes(
                Bucket=s3_params.bucket_name, 
                Key=s3_fpath, 
                ObjectAttributes=["ObjectSize"]
            ).get("ObjectSize")
        except Exception as e:
            logger.warning(f"Encountered Error Trying to Get Object Total Size for {s3_fpath}. {e}")
            object_size = None

        # tracking download progress
        curr_transferred = 0
        def _custom_progress_callback(chunk_size: int):
            nonlocal curr_transferred
            nonlocal object_size
            curr_transferred += chunk_size
            # call passed in progress callback function
            progress_callback(curr_transferred, object_size)

        callback = _custom_progress_callback

    # default return data to None
    buffer = BytesIO()
    s3_client.download_fileobj(
        s3_params.bucket_name, 
        s3_fpath, 
        buffer, 
        Callback=callback,
        Config=transfer_config
    )
    buffer.seek(0)
    # BytesIO
    if bytes_io: data, buffer = buffer, None
    # bytes
    else: data, buffer = buffer.getvalue(), None

    return data


@manage_s3_session
def get_s3_file_disk(
    s3_fpath: str, 
    save_path: str,
    s3_client = None,
    s3_params: S3Params = None,
    progress_callback: Callable[[int, int], any] = None,
    transfer_config: TransferConfig = TransferConfig(max_concurrency=3),
    **kwargs
) -> Union[str, None]:
    """Function to upload data object to s3 using `boto3.s3.download_file()`

    :param s3_fpath: key to s3 file to download
    :param save_path: string file path to save data to file on disk
    :param s3_client: provided s3 client object, defaults to None
    :param s3_params: provided instance of S3Params, defaults to None
    :param progress_callback: user-defined custom progress callback that is called throughout the download process that takes as input \
        (current number of bytes downloaded so far, total number of bytes to download)
    :param transfer_config: instance of \
        [boto3.s3.transfer.TransferConfig](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/customizations/s3.html#boto3.s3.transfer.TransferConfig),\
        defaults to boto3.s3.transfer.TransferConfig(max_concurrency=3)
    :return: string file path to locally saved file on disk
    """
    logger.info(f"get_s3_file_disk(): {s3_fpath}")
    
    # validate that fpath is of type string
    assert isinstance(save_path, str)
    
    # handle progress callback
    callback = None
    if progress_callback:        
        try:
            # get size of object to read in
            object_size = s3_client.get_object_attributes(
                Bucket=s3_params.bucket_name, 
                Key=s3_fpath, 
                ObjectAttributes=["ObjectSize"]
            ).get("ObjectSize")
        except Exception as e:
            logger.warning(f"Encountered Error Trying to Get Object Total Size for {s3_fpath}. {e}")
            object_size = None

        # tracking download progress
        curr_transferred = 0
        def _custom_progress_callback(chunk_size: int):
            nonlocal curr_transferred
            nonlocal object_size
            curr_transferred += chunk_size
            # call passed in progress callback function
            progress_callback(curr_transferred, object_size)

        callback = _custom_progress_callback
    
    # call s3 upload
    s3_client.download_file(
        s3_params.bucket_name,
        s3_fpath,
        save_path,
        Callback=callback,
        Config=transfer_config
    )

    # validate that saved file is an existing file path
    assert os.path.exists(save_path)
    
    return save_path


@manage_s3_session
def get_s3_file( 
    s3_fpath: str, 
    save_path: Union[str, None] = None,
    s3_client = None,
    s3_params: S3Params = None,
    progress_callback: Callable[[int, int], any] = None,
    transfer_config: TransferConfig = TransferConfig(max_concurrency=3),
    bytes_io: bool = False,
    **kwargs
) -> Union[BytesIO, bytes, str, None]:
    """Function to downlad a given s3 file using either: `get_s3_file_simple()`, `get_s3_file_transfer()`, `get_s3_file_disk()`.
    Falls back to `get_s3_file_chunked()` if `get_s3_file_simple()` or `get_s3_file_transfer()` fail.

    :param s3_fpath: key to s3 file to download
    :param save_path: string file path to save data to, defaults to None
    :param s3_client: provided s3 client object, defaults to None
    :param s3_params: provided instance of S3Params, defaults to None
    :param progress_callback: user-defined custom progress callback that is called throughout the download process that takes as input \
        (current number of bytes downloaded so far, total number of bytes to download)
    :param transfer_config: instance of \
        [boto3.s3.transfer.TransferConfig](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/customizations/s3.html#boto3.s3.transfer.TransferConfig),\
        defaults to boto3.s3.transfer.TransferConfig(max_concurrency=3)
    :param bytes_io: flag to convert pulled object as BytesIO instance, defaults to False
    :return: either bytes object, BytesIO object, string path to saved file, or None
    """
    global performance_manager

    ## If save_path is specified and is of type string
    # then, call `get_s3_file_disk()` directly
    # Note: this method of downloading does not keep track of historical throughput performance
    if save_path and isinstance(save_path, str):
        # start upload
        start = time.time()
        ret = get_s3_file_disk(
            s3_fpath,
            save_path,
            s3_params=s3_params,
            s3_client=s3_client,
            progress_callback=progress_callback,
            transfer_config=transfer_config,
            **kwargs
        )
        total_seconds = time.time() - start
        
        # `save_path` should be an existing file path
        assert os.path.exists(ret)
        n_bytes = os.path.getsize(ret)
        mb = n_bytes / MB
        mbps = mb / total_seconds
        mbps = round(mbps, 2)
        logger.debug(f"get_s3_file_disk() <{round(mb, 4)}mb, {round(total_seconds, 3)}s, {mbps}mbps>: {s3_fpath}")
        
        return ret

    # default return data to None
    data = None
    try:
        # start download
        start = time.time()
        perf_type = "download"

        # choose the right function to run
        chosen_func = performance_manager.choose_function(perf_type)

        # call appropriate function
        if chosen_func == "simple":
            data = get_s3_file_simple(s3_fpath, s3_params=s3_params, s3_client=s3_client, bytes_io=bytes_io, **kwargs)
        elif chosen_func == "transfer":
            data = get_s3_file_transfer(
                s3_fpath, 
                s3_params=s3_params, 
                s3_client=s3_client, 
                progress_callback=progress_callback, 
                transfer_config=transfer_config, 
                bytes_io=bytes_io, 
                **kwargs
            )
        # calculate updates for performance dict
        total_seconds = time.time() - start
        n_bytes = 0.0
        if isinstance(data, BytesIO): n_bytes = data.getbuffer().nbytes
        elif isinstance(data, bytes): n_bytes = len(data)
        elif isinstance(data, memoryview): n_bytes = data.nbytes               
        # update performance dict in a thread-safe manner
        with threading_lock:
            performance_manager.update_performance_record(perf_type, n_bytes, total_seconds)
            mbps = performance_manager.records_dict[perf_type].metrics[chosen_func][-1].mbps
        
        logger.debug(f"get_s3_{chosen_func}() <{round(n_bytes/MB, 4)}mb, {round(total_seconds, 3)}s, {mbps}mbps>: {s3_fpath}")

    except Exception as e:
        logger.warning(f"Caught Exception: {e}")
        logger.info(f"Failed to read S3 object: {s3_fpath}. Falling back to reading in chunks ...")
        logger.info(f"Attempting to read S3 File in Chunks from {s3_fpath}")
        data = get_s3_file_chunked(
            s3_fpath, 
            s3_params=s3_params,
            progress_callback=progress_callback,
            bytes_io=bytes_io,
            **kwargs
        )
        
    return data
    

@manage_s3_session
def get_s3_image(
    s3_fpath: str, 
    s3_client = None,
    s3_params: Optional[S3Params] = None,
    img_format: Optional[ImageFormatType] = None,
    bytes_io: bool = False,
    **kwargs 
) -> Union[BytesIO, Image.Image, np.ndarray, str, bytes, None]:
    """Function to retrieve an image from S3. 
    Calls `get_s3_file()` so you can also pass in additional kwargs through to that function.

    Formatting Hierarchy Logic: `img_format` > `bytes_io`
    1. Check for img_format args
    2. Then check for bytes_io arg
    3. If neither provided return raw output of s3_object.read()

    :param s3_fpath: key to s3 file to download
    :param s3_client: provided s3 client object, defaults to None
    :param s3_params: provided instance of S3Params, defaults to None
    :param img_format: one of ImageFormatType enum, defaults to None
    :param bytes_io: flag to convert pulled object as BytesIO instance, defaults to False
    :return: an instance of either BytesIO, PIL.Image.Image, np.ndarray, string, bytes, or None
    """
    logger.info(f"get_s3_image(): {s3_fpath}")
    ## Format functions
    def _get_base64_html_string(s3_fpath: str) -> str:
        # Get image file
        object_data: BytesIO = get_s3_file(
            s3_fpath, 
            s3_client=s3_client, 
            s3_params=s3_params,
            bytes_io=True,
            **kwargs
        )
        # if using base64 encoding
        extension = os.path.splitext(s3_fpath)[1].lower()
        extension_dict = {
            ".jpg": 'data:image/jpeg;base64,',
            ".jpeg": 'data:image/jpeg;base64,',
            ".png": 'data:image/png;base64,',
            ".gif": 'data:image/gif;base64,'
        }
        if extension not in extension_dict: 
            return
        image_string = extension_dict[extension]
        image_string += base64.b64encode(object_data.read()).decode('utf-8')
        return image_string

    def _get_pil_image(s3_fpath: str) -> Image.Image:
        # Get image file
        object_data: BytesIO = get_s3_file(
            s3_fpath, 
            s3_client=s3_client, 
            s3_params=s3_params,
            bytes_io=True,
            **kwargs
        )
        with Image.open(object_data) as img:
            img.load()
        return img
    
    def _get_np_array_image(s3_fpath: str) -> np.ndarray:
        # Get image file
        object_data: BytesIO = get_s3_file(
            s3_fpath, 
            s3_client=s3_client, 
            s3_params=s3_params,
            bytes_io=True,
            **kwargs
        )
        img = np.array(_get_pil_image(object_data))
        return img

    def _get_bytesio_image(s3_fpath: str) -> BytesIO:
        # Get image file
        object_data: BytesIO = get_s3_file(
            s3_fpath, 
            s3_client=s3_client, 
            s3_params=s3_params,
            bytes_io=True,
            **kwargs
        )
        return object_data
    
    # functions dictionary
    format_funcs_dict = {
        ImageFormatType.BASE64_HTML_STRING: _get_base64_html_string,
        ImageFormatType.PIL_IMAGE: _get_pil_image,
        ImageFormatType.NUMPY_ARRAY: _get_np_array_image,
        "bytes_io": _get_bytesio_image
    }

    ## Hierarchy of Logic: `img_format` > `bytes_io`
    # first check for img_format args
    # then check for bytes_io arg
    # if nothing provided return raw output of s3_object.read()
    if img_format in format_funcs_dict: return format_funcs_dict[img_format](s3_fpath)
    if bytes_io: return format_funcs_dict['bytes_io'](s3_fpath)

    return get_s3_file(s3_fpath, bytes_io=False, **kwargs)


@manage_s3_session
def get_s3_files_generator(
    key_list: List[str], 
    s3_client = None,
    s3_params: S3Params = None,
    bytes_io: bool = False,
    **kwargs
) -> Generator[Union[BytesIO, bytes, None], Any, None]:
    """Generator function to quickly loop through reading a list of s3 file keys.
    Calls `get_s3_file()` so you can also pass in additional kwargs through to that function.

    :param key_list: list of s3 keys
    :param s3_client: provided s3 client object, defaults to None
    :param s3_params: provided instance of S3Params, defaults to None
    :param bytes_io: flag to convert pulled object as BytesIO instance, defaults to False
    :return: None
    :yield: either BytesIO object, bytes object, or None
    """
    logger.info(f"get_s3_files_generator(): {key_list}")
    for key in key_list: 
        yield get_s3_file(key, s3_client=s3_client, s3_params=s3_params, bytes_io=bytes_io, **kwargs)
    return


@manage_s3_session
def get_s3_files_batch(
    key_list: List[str],
    s3_client = None,
    s3_params: S3Params = None, 
    max_concurrency: int = 0, 
    bytes_io: bool = False,
    **kwargs
) -> list:
    """Function to read a list of s3 file keys and return a batch data. Can use multithreading as well.
    Calls `get_s3_file()` when `max_concurrency=0` so you can also pass in additional kwargs through to that function.

    :param key_list:  list of s3 keys
    :param s3_client: provided s3 client object, defaults to None
    :param s3_params: provided instance of S3Params, defaults to None
    :param max_concurrency: max no. of concurrent threads to use when downloading multiple files (0 means no concurrency), defaults to 0
    :param bytes_io: flag to convert pulled object as BytesIO instance, defaults to False
    :return: either pulled S3 object or BytesIO object
    """
    logger.info(f"get_s3_files_batch(): {key_list}")
    count = 0

    count_lock = threading.Lock()

    def _download_file(s3_client, s3_params: S3Params, s3_fpath: str):
        nonlocal count
        obj = s3_client.get_object(Bucket=s3_params.bucket_name, Key=s3_fpath)
        obj = obj['Body'].read()
        if bytes_io: 
            obj = BytesIO(obj)
            obj.seek(0)

        with count_lock:
            count +=1
        
        logger.debug(f"Completed Downloading from S3 (in batch): {count}/{len(key_list)}")
        
        return obj
    
    # Iterative batch mode
    if not max_concurrency or max_concurrency < 1:
        objs = []
        for k in key_list: 
            objs.append(
                get_s3_file(k, s3_params=s3_params, s3_client=s3_client, bytes_io=bytes_io, **kwargs)
            )
        return objs
    
    # Multithreading batch mode
    args = [(a,) for a in key_list]
    objs = []
    with ThreadPoolExecutor(max_workers=max_concurrency) as executor:
        for obj in executor.map(lambda p: _download_file(s3_client, s3_params, *p), args):
            objs.append(obj)
    
    return objs 


@manage_s3_session
def list_s3_folders(
    prefix: str,
    s3_client = None,
    s3_params: S3Params = None,
    delimiter: str ='/',
    **kwargs
) -> List[str]:
    """Function to get list of valid folders within S3 Bucket Prefix
    
    :param prefix: S3 Bucket Path Prefix
    :param s3_client: provided s3 client object, defaults to None
    :param s3_params: provided instance of S3Params, defaults to None
    :param delimiter: delimiter used to filter objects in S3 (e.g. only subfolders - delimiter="/"), defaults to '/'
    :return: List of S3 Object Keys
    """
    # Adding trailing slash if looking for "directory"
    if prefix.strip() != "" and not prefix.endswith("/"):
        old_prefix = prefix
        prefix = f"{prefix}/"
        logger.debug(f"Old Prefix {old_prefix} -> New Prefix: {prefix}")

    logger.debug(f"list_s3_folders(): {prefix}")

    folders = []

    paginator = s3_client.get_paginator('list_objects_v2')
    page_iterator = paginator.paginate(
        Bucket=s3_params.bucket_name,
        Prefix=prefix,
        Delimiter=delimiter, 
        PaginationConfig={"PageSize": 100}
    )
    for page in page_iterator:
        if "CommonPrefixes" not in page: continue
        prefixes = [pref_dict['Prefix'] for pref_dict in page['CommonPrefixes']]
        folders.extend(prefixes)
    return folders


@manage_s3_session
def get_valid_s3_keys(
    prefix: str,
    ignore: List[str] = [".DS_Store"],
    filter_extensions: List[str] = [],
    s3_client = None,
    s3_params: S3Params = None,
    **kwargs
) -> List[str]:
    """Function to get list of valid keys within S3 Bucket Path
    
    :param prefix: S3 Bucket Path Prefix
    :param ignore: list of directories/prefixes and filepaths to ignore, defaults to ['.DS_Store']
    :param filter_extensions: list of file extensions to filter for (empty list means get everything), defaults to []
    :param s3_client: provided s3 client object, defaults to None
    :param s3_params: provided instance of S3Params, defaults to None
    :return: List of S3 Object Keys
    """
    # Adding trailing slash if looking for "directory"
    if prefix.strip() != "" and not prefix.endswith("/"):
        old_prefix = prefix
        prefix = f"{prefix}/"
        logger.debug(f"Old Prefix {old_prefix} -> New Prefix: {prefix}")
    
    ignore = set(ignore)

    logger.debug(f"get_valid_s3_keys(): {prefix}")
    
    valid_keys = []

    bucket_kwargs = {
        "Bucket": s3_params.bucket_name, 
        "Prefix": prefix,
    }
    while True:
        resp = s3_client.list_objects_v2(**bucket_kwargs)
        for obj in resp["Contents"]: valid_keys.append(obj["Key"])
        if "NextContinuationToken" not in resp: break
        bucket_kwargs['ContinuationToken'] = resp["NextContinuationToken"]
    
    # Process keys based on ignore_dirs and filter_extensions
    li = []
    for fpath in valid_keys:
        parts = fpath.strip("/").split("/")
        fname = parts[-1]

        # check if ignored
        ignored = False
        for part in parts:
            if part in ignore:
                ignored = True
                break
        
        # check if file extension supported
        # if filter_extensions is empty list -- default to supporting all extensions
        supported_extension = False
        if len(filter_extensions) < 1:
            supported_extension = True
        else:
            for extension in filter_extensions:
                if fname.endswith(extension):
                    supported_extension = True
            
        # only append if not ignored and extension supported
        if not ignored and supported_extension: 
            li.append(fpath)
    
    fpaths, li = li, None
    return fpaths


@manage_s3_session
def key_exists_s3(
    key: str, 
    s3_client = None, 
    s3_params: S3Params = None,
    **kwargs
) -> bool:
    """Function to see if key exists in S3

    :param key: key fpath string
    :param s3_client: provided s3 client object, defaults to None
    :param s3_params: provided instance of S3Params, defaults to None
    :return: True if key exists, False otherwise
    """
    logger.debug(f"key_exists_s3(): {key}")
    try:
        s3_client.head_object(Bucket=s3_params.bucket_name, Key=key)
        return True
    except ClientError as ce:
        if ce.response["Error"]["Code"] == "404":
            return False
        raise


@manage_s3_session
def upload_to_s3_simple(
    data: Union[bytes, memoryview, BytesIO], 
    save_key: str, 
    s3_client = None, 
    s3_params: S3Params = None,
    **kwargs
) -> str:
    """Function to upload data object to s3 using `boto3.s3.put_object()`

    :param data: data to save as bytes, memoryview, or BytesIO
    :param save_key: s3 key to save the data to
    :param s3_client: provided s3 client object, defaults to None
    :param s3_params: provided instance of S3Params, defaults to None
    :raises Exception: General exception if not HTTP Status Code 200
    :return: S3 key of uploaded object if successful
    """
    logger.info(f"upload_to_s3_simple(): {save_key}")
    # if data is BytesIO convert to bytes
    if isinstance(data, BytesIO): data = data.getvalue()
    if not isinstance(data, (bytes, memoryview)):
        raise Exception(f"UploadToS3Error: data is not of instance 'bytes' or 'memoryview' for {save_key}.")
    
    # upload
    response = s3_client.put_object(
        Body=data,
        Bucket=s3_params.bucket_name,
        Key=save_key
    )
    if response.get('ResponseMetadata', {}).get('HTTPStatusCode', 400) == 200:
        return save_key

    raise Exception(f'Error writing object to S3')


@manage_s3_session
def upload_to_s3_transfer(
    data: Union[bytes, memoryview, BytesIO], 
    save_key: str, 
    s3_client = None, 
    s3_params: S3Params = None,
    progress_callback: Callable[[int, int], any] = None,
    transfer_config: TransferConfig = TransferConfig(max_concurrency=3),
    **kwargs
) -> str:
    """Function to upload data object to s3 using `boto3.s3.upload_fileobj()`

    :param data: data to save/write - can be bytes, memoryview, BytesIO
    :param save_key: s3 key to save the data to
    :param s3_client: provided s3 client object, defaults to None
    :param s3_params: provided instance of S3Params, defaults to None
    :param progress_callback: user-defined custom progress callback that is called throughout the download process that takes as input \
        (current number of bytes uploaded so far, total number of bytes to download)
    :param transfer_config: instance of \
        [boto3.s3.transfer.TransferConfig](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/customizations/s3.html#boto3.s3.transfer.TransferConfig),\
        defaults to boto3.s3.transfer.TransferConfig(max_concurrency=3)
    :return: S3 key of uploaded object if successful
    """
    logger.info(f"upload_to_s3_transfer(): {save_key}")
    # if data is BytesIO convert to bytes
    if isinstance(data, BytesIO): data = data.getvalue()
    if not isinstance(data, (bytes, memoryview)):
        raise Exception(f"UploadToS3Error: data is not of instance 'bytes' or 'memoryview' for {save_key}.")
    
    # handle progress callback
    callback = None
    if progress_callback:        
        # get size of object to upload
        object_size = len(data)
        # tracking download progress
        curr_transferred = 0
        def _custom_progress_callback(chunk_size: int):
            nonlocal curr_transferred
            nonlocal object_size
            curr_transferred += chunk_size
            # call passed in progress callback function
            progress_callback(curr_transferred, object_size)

        callback = _custom_progress_callback
    
    # call s3 upload
    s3_client.upload_fileobj(
        BytesIO(data),
        s3_params.bucket_name,
        save_key,
        Callback=callback,
        Config=transfer_config
    )

    return save_key


@manage_s3_session
def upload_to_s3_file(
    fpath: str,
    save_key: str, 
    s3_client = None, 
    s3_params: S3Params = None,
    progress_callback: Callable[[int, int], any] = None,
    transfer_config: TransferConfig = TransferConfig(max_concurrency=3),
    **kwargs
) -> str:
    """Function to upload data object to s3 using `boto3.s3.upload_file()`

    :param fpath: string file path to upload to S3
    :param save_key: s3 key to save the data to
    :param s3_client: provided s3 client object, defaults to None
    :param s3_params: provided instance of S3Params, defaults to None
    :param progress_callback: user-defined custom progress callback that is called throughout the download process that takes as input \
        (current number of bytes uploaded so far, total number of bytes to download)
    :param transfer_config: instance of \
        [boto3.s3.transfer.TransferConfig](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/customizations/s3.html#boto3.s3.transfer.TransferConfig),\
        defaults to boto3.s3.transfer.TransferConfig(max_concurrency=3)
    :raises Exception: AssertionError if fpath is not string or if fpath does not exist
    :return:  S3 key of uploaded object if successful
    """
    logger.info(f"upload_to_s3_file(): {save_key}")
    # validate that fpath is of type string and that it is an existing file path
    assert isinstance(fpath, str)
    assert os.path.exists(fpath)
    
    # handle progress callback
    callback = None
    if progress_callback:        
        # get size of object to upload
        object_size = os.path.getsize(fpath)
        # tracking upload progress
        curr_transferred = 0
        def _custom_progress_callback(chunk_size: int):
            nonlocal curr_transferred
            nonlocal object_size
            curr_transferred += chunk_size
            # call passed in progress callback function
            progress_callback(curr_transferred, object_size)

        callback = _custom_progress_callback

    # call s3 upload
    s3_client.upload_file(
        fpath,
        s3_params.bucket_name,
        save_key,
        Callback=callback,
        Config=transfer_config
    )

    return save_key


@manage_s3_session
def upload_to_s3_folder(
    dirpath: str,
    save_prefix: str, 
    ignore: List[str] = [".DS_Store", "MACOSX"], 
    s3_client = None, 
    s3_params: S3Params = None,
    progress_callback: Callable[[int, int], any] = None,
    transfer_config: TransferConfig = TransferConfig(max_concurrency=3),
    **kwargs
) -> List[str]:
    """Function to upload data object to s3 using `boto3.s3.upload_file()`

    :param dirpath: string file path to upload to S3
    :param save_prefix: s3 prefix to save contents of folder to
    :param ignore: list of string file names to ignore, defaults to [".DS_Store", "MACOSX"]
    :param s3_client: provided s3 client object, defaults to None
    :param s3_params: provided instance of S3Params, defaults to None
    :param progress_callback: user-defined custom progress callback that is called throughout the download process that takes as input \
        (current number of bytes uploaded so far, total number of bytes to download)
    :param transfer_config: instance of \
        [boto3.s3.transfer.TransferConfig](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/customizations/s3.html#boto3.s3.transfer.TransferConfig),\
        defaults to boto3.s3.transfer.TransferConfig(max_concurrency=3)
    :raises Exception: AssertionError if fpath is not string or if fpath does not exist
    :return: list of saved s3 keys
    """
    logger.info(f"upload_to_s3_folder(): {dirpath} -> {save_prefix}")

    # validate that dirpath is of type string and that it is an existing dir path
    assert isinstance(dirpath, str)
    assert os.path.exists(dirpath)
    assert os.path.isdir(dirpath)

    # list of successfully uploaded S3 keys
    ret = []

    for root, dirs, files in os.walk(dirpath):
        for file in files:
            # ignore certain file names
            if file in ignore: continue
            local_path = os.path.join(root, file)
            # create S3 key by removing the local base path and prepending the prefix
            relative_path = os.path.relpath(local_path, dirpath)
            # ensure S3 key uses forward slashes
            s3_key = os.path.join(save_prefix, relative_path).replace("\\", "/")
            ret_key = upload_to_s3_file(
                local_path, 
                s3_key, 
                s3_params=s3_params,
                s3_client=s3_client,
                progress_callback=progress_callback,
                transfer_config=transfer_config,
                **kwargs
            )
            ret.append(ret_key)
    
    return ret


@manage_s3_session
def upload_to_s3(
    data: Union[bytes, memoryview, BytesIO, str], 
    save_path: str, 
    s3_client = None, 
    s3_params: S3Params = None,
    progress_callback: Callable[[int, int], any] = None,
    transfer_config: TransferConfig = TransferConfig(max_concurrency=3),
    **kwargs
) -> Union[str, List[str]]:
    """Function to upload data object to s3 using either: `upload_to_s3_simple()` or `upload_to_s3_transfer()`.

    :param data: data to save/write - can be bytes, memoryview, BytesIO, or string file or directory path
    :param save_path: s3 key or prefix to save the data to
    :param s3_client: provided s3 client object, defaults to None
    :param s3_params: provided instance of S3Params, defaults to None
    :param progress_callback: user-defined custom progress callback that is called throughout the download process that takes as input \
        (current number of bytes uploaded so far, total number of bytes to download)
    :param transfer_config: instance of \
        [boto3.s3.transfer.TransferConfig](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/customizations/s3.html#boto3.s3.transfer.TransferConfig),\
        defaults to boto3.s3.transfer.TransferConfig(max_concurrency=3)
    :raises Exception: General exception if not HTTP Status Code 200 or input data is not of right type
    :return: either single S3 key or list of S3 keys of uploaded object(s) if successful
    """
    global performance_manager

    # if data is BytesIO convert to bytes
    if isinstance(data, BytesIO): data = data.getvalue()
    # validate type of input data
    if not isinstance(data, (bytes, memoryview, str)):
        raise Exception(f"UploadToS3Error: input data is not of type 'bytes', 'memoryview', or 'string' for {save_path}.")

    ## If data is of type string, validate that the string is a correct file or dirpath
    # then, call `upload_to_s3_file()` or `upload_to_s3_folder()` directly
    # Note: this method of uploading does not keep track of historical throughput performance
    if isinstance(data, str):
        # `data` here should be an existing file path or dir path
        assert os.path.exists(data)

        # start upload
        start = time.time()

        if os.path.isfile(data):
            ret = upload_to_s3_file(
                data,
                save_path,
                s3_params=s3_params,
                s3_client=s3_client,
                progress_callback=progress_callback,
                transfer_config=transfer_config,
                **kwargs
            )
        elif os.path.isdir(data):
            ret = upload_to_s3_folder(
                data,
                save_path,
                s3_params=s3_params,
                s3_client=s3_client,
                progress_callback=progress_callback,
                transfer_config=transfer_config,
                **kwargs
            )
        
        # end upload
        total_seconds = time.time() - start
        n_bytes = os.path.getsize(data)
        mb = n_bytes / MB
        mbps = mb / total_seconds
        mbps = round(mbps, 2)
        logger.debug(f"upload_to_s3_file() <{round(mb, 4)}mb, {round(total_seconds, 3)}s, {mbps}mbps>: {save_path}")
        
        return ret

    ## Else if data is of type bytes or memoryview, run upload with performance manager
    # default return
    ret = None

    # start upload
    start = time.time()
    perf_type = "upload"

    # choose the right function to run
    chosen_func = performance_manager.choose_function(perf_type)

    try:
        # call appropriate function
        if chosen_func == "simple":
            ret = upload_to_s3_simple(data, save_path, s3_params=s3_params, s3_client=s3_client, **kwargs)
        elif chosen_func == "transfer":
            ret = upload_to_s3_transfer(
                data, 
                save_path, 
                s3_params=s3_params, 
                s3_client=s3_client, 
                progress_callback=progress_callback, 
                transfer_config=transfer_config, 
                **kwargs
            )
    except Exception as e:
        logger.info(f"Encountered Error Trying to Upload Object: {save_path}. {e}")
        logger.info(f"Falling back to upload_to_s3_transfer() ... {save_path}")
        # override previously chosen function
        chosen_func = "transfer"
        performance_manager.override_chosen_func(perf_type, chosen_func)
        # call upload_to_s3_transfer()
        ret = upload_to_s3_transfer(
            data, 
            save_path, 
            s3_params=s3_params, 
            s3_client=s3_client, 
            progress_callback=progress_callback, 
            transfer_config=transfer_config, 
            **kwargs
        )
    finally:
        # update performance dict
        total_seconds = time.time() - start
        n_bytes = 0.0
        if isinstance(data, BytesIO): n_bytes = data.getbuffer().nbytes
        elif isinstance(data, bytes): n_bytes = len(data)
        elif isinstance(data, memoryview): n_bytes = data.nbytes
        # update performance dict in a thread-safe manner
        with threading_lock:
            performance_manager.update_performance_record(perf_type, n_bytes, total_seconds)
            mbps = performance_manager.records_dict[perf_type].metrics[chosen_func][-1].mbps
        
        logger.debug(f"upload_to_s3_{chosen_func}() <{round(n_bytes/MB, 4)}mb, {round(total_seconds, 3)}s, {mbps}mbps>: {save_path}")

    return ret
    

@manage_s3_session
def delete_s3_object(
    key: str, 
    s3_client = None, 
    s3_params: S3Params = None,
    del_prefix: bool = False,
    **kwargs
) -> bool:
    """Function to delete an object from s3 based on its key

    :param key: s3 key of object to delete
    :param s3_client: provided s3 client object, defaults to None
    :param s3_params: provided instance of S3Params, defaults to None
    :param del_prefix: flag to define if being used as part of deleting prefix function, defaults to False
    :return: True if delete successful, else return False
    """
    if not del_prefix:
        logger.info(f"delete_s3_object(): {key}")
    
    key_exists_before = key_exists_s3(key, s3_client=s3_client, s3_params=s3_params)
    try:
        # delete object
        response = s3_client.delete_object(Bucket=s3_params.bucket_name, Key=key)
        key_exists_after = key_exists_s3(key, s3_client=s3_client, s3_params=s3_params)
        # if key exists before but not after, we know it has been deleted and we can return True
        if key_exists_before and not key_exists_after: return True
    except Exception as e:
        logger.warning(f"Failed to delete S3 object: {key}")
    
    return False


@manage_s3_session
def delete_s3_objects_by_prefix(
    prefix: str, 
    s3_client = None, 
    s3_params: S3Params = None,
    **kwargs
) -> List[str]:
    """Function to delete all objects in S3 bucket that share a given prefix

    :param prefix: S3 Bucket Path Prefix
    :param s3_client: provided s3 client object, defaults to None
    :param s3_params: provided instance of S3Params, defaults to None
    :return: List of S3 Object Keys that were successfully delete
    """
    logger.info(f"delete_s3_objects_by_prefix(): {prefix}")   
    # Adding trailing slash if looking for "directory"
    if prefix.strip() != "" and not prefix.endswith("/"):
        old_prefix = prefix
        prefix = f"{prefix}/"
        logger.debug(f"Old Prefix {old_prefix} -> New Prefix: {prefix}")


    deleted_keys: List[str]= []

    try:
        # get list of valid keys using input prefix
        valid_keys = get_valid_s3_keys(prefix, s3_client=s3_client, s3_params=s3_params)
        num_keys = len(valid_keys)

        # iteratively delete keys
        for i, key in enumerate(valid_keys):
            is_deleted = delete_s3_object(key, s3_client=s3_client, s3_params=s3_params, del_prefix=True)
            # if successfully deleted print message and add to deleted_keys list
            if is_deleted:
                logger.debug(f"Deleted S3 file: {i+1}/{num_keys} -- {key}")
                deleted_keys.append(key)
    except Exception as e:
        logger.warning(f"Failed to delete S3 object by prefix: {prefix}")
        
    return deleted_keys


@manage_s3_session
def _extract_archive_upload_to_s3(
    fpath: str, 
    save_prefix: str,
    archive_file_key: str,
    cleanup_local: bool = False, 
    cleanup_bucket: bool = False, 
    s3_client = None,
    s3_params: S3Params =  None,
    progress_callback: Callable[[int, int], any] = None,
    transfer_config: TransferConfig = TransferConfig(max_concurrency=3),
    **kwargs
) -> List[str]:
    """Function to extract archive file locally and upload contents back to S3. 
   
    File Type Support:
    - .zip
    - .tar
    - .tar.gz

    :param fpath: local file path to archive file
    :param save_prefix: directory to prefix the extracted archive
    :param archive_file_key: s3 key of archive file that is being extracted
    :param cleanup_local: flag to remove extracted contents of archive file locally at the end of this function call, defaults to False
    :param cleanup_bucket: flag to remove the archive file in S3 after successful upload of extracted contents, defaults to False
    :param s3_client: provided s3 client object, defaults to None
    :param s3_params: provided instance of S3Params, defaults to None
    :param progress_callback: user-defined custom progress callback that is called throughout the download process that takes as input \
        (current number of bytes uploaded so far, total number of bytes to download)
    :param transfer_config: instance of \
        [boto3.s3.transfer.TransferConfig](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/customizations/s3.html#boto3.s3.transfer.TransferConfig),\
        defaults to boto3.s3.transfer.TransferConfig(max_concurrency=3)
    :return: list of saved s3 keys
    """
    logger.info(f"extract_upload_to_s3(): {fpath} -> {save_prefix}")
    
    # create tmp directory if does not already exist
    temp_dir = "tmp"
    path = pathlib.Path(temp_dir)
    path.mkdir(exist_ok=True)

    if not (fpath.endswith(".zip") or fpath.endswith(".tar") or fpath.endswith(".tar.gz")):
        raise ValueError(f"Expected archive file path to end in '.tar', '.tar.gz', or '.zip` file extension")

    # intialize return list of successfully uploaded S3 Keys
    ret = []

    # create extract_to dirpath within tmp
    if fpath.endswith(".zip"):
        fname = os.path.basename(fpath).split(".zip")[0]
    elif fpath.endswith(".tar"):
        fname = os.path.basename(fpath).split(".tar")[0]
    elif fpath.endswith(".tar.gz"):
        fname = os.path.basename(fpath).split(".tar.gz")[0]
    
    extract_to_path = os.path.join(temp_dir, fname)
    
    # extract the archive file
    local_archive_dirpath = extract_archive_file(fpath, extract_to_path)
    
    # upload to S3
    ret = upload_to_s3_folder(
        local_archive_dirpath, 
        save_prefix,
        s3_client=s3_client,
        s3_params=s3_params,
        progress_callback=progress_callback,
        transfer_config=transfer_config,
        **kwargs
    )

    ## cleanup 
    # delete extracted dir if flag passed in and dirpath exists
    if cleanup_local:
        try:
            if os.path.exists(local_archive_dirpath) and os.path.isdir(local_archive_dirpath):
                shutil.rmtree(local_archive_dirpath)
            os.remove(fpath)
        except Exception as e:
            logger.warning(f"Caught Error trying to remove {local_archive_dirpath}: {e}")
    
    if cleanup_bucket:
        delete_s3_object(
            archive_file_key,
            s3_client=s3_client,
            s3_params=s3_params,
        )
    
    return ret


@manage_s3_session
def extract_archive_file_s3(
    key: str, 
    save_prefix: str,
    cleanup_local: bool = False, 
    cleanup_bucket: bool = False,
    s3_params: S3Params =  None,
    s3_client = None, 
    progress_callback: Callable[[int, int], any] = None,
    transfer_config: TransferConfig = TransferConfig(max_concurrency=3),
    **kwargs
) -> str:
    """Function to extract archive file in S3

    File Type Support:
    - .zip
    - .tar
    - .tar.gz

    :param key: key to archive file
    :param save_prefix: directory to prefix the extracted archive
    :param cleanup_local: flag to remove extracted contents of archive file locally at the end of this function call, defaults to False
    :param cleanup_bucket: flag to remove the archive file in S3 after successful upload of extracted contents, defaults to False
    :param s3_client: provided s3 client object, defaults to None
    :param s3_params: provided instance of S3Params, defaults to None
    :param progress_callback: user-defined custom progress callback that is called throughout the download process that takes as input \
        (current number of bytes uploaded so far, total number of bytes to download)
    :param transfer_config: instance of \
        [boto3.s3.transfer.TransferConfig](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/customizations/s3.html#boto3.s3.transfer.TransferConfig),\
        defaults to boto3.s3.transfer.TransferConfig(max_concurrency=3)
    :return: prefix path to directory where extracted archive contents exist
    """
    
    logger.info(f"extract_archive_file_s3(): {key}")

    # path to local archived file
    fname = os.path.basename(key)
    archive_fpath = os.path.join("tmp", fname)
    
    # create tmp directory if does not already exist
    path = pathlib.Path(archive_fpath)
    path.parent.mkdir(exist_ok=True, parents=True)

    # read in compressed archive file
    archive_fpath = get_s3_file(
        key,
        save_path=archive_fpath, 
        s3_client=s3_client, 
        s3_params=s3_params
    )

    # handle different compressions
    new_keys = []
    new_keys = _extract_archive_upload_to_s3(
        archive_fpath, 
        save_prefix,
        key,
        cleanup_local=cleanup_local,
        cleanup_bucket=cleanup_bucket,
        s3_params=s3_params,
        s3_client=s3_client,
        progress_callback=progress_callback,
        transfer_config=transfer_config,
        **kwargs
    )

    logger.debug(f"New Extracted Keys: {new_keys[:10]}, ... +{len(new_keys)-10}")

    # get archive dir
    if len(new_keys) < 1:
        logger.warning(f"WARNING: extract_archive_file_s3() resulted in 0 Extracted Keys!")
        return
    
    # make sure save_prefix ends with trailing "/" - this is required for S3
    if not save_prefix.endswith("/"):
        save_prefix = f"{save_prefix}/"
    
    # return the s3 prefix path where data has been extracted
    return save_prefix

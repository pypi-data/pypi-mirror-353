import typing
import logging
import time
import uuid
import sys
import socket
import pickle
import zlib
import ssl
from io import BytesIO

try:
    import resource
except ImportError:
    # No windows support for this lib
    resource = None

from inspect import signature, Parameter, isgeneratorfunction, isgenerator

try:
    from StringIO import StringIO
except ImportError:
    from io import StringIO

from .exceptions import ImproperlyConfigured
from .constants import EMPTY, BATCH_PROCESSOR_TYPE

if typing.TYPE_CHECKING:
    from .base import EventBase
    from .pipeline import Pipeline

logger = logging.getLogger(__name__)


def _extend_recursion_depth(limit: int = 1048576):
    """
    Extends the maximum recursion depth of the Python interpreter.

    Args:
        limit: The new recursion depth limit. Defaults to 1048576.

    This function adjusts the system’s recursion limit to allow deeper recursion
    in cases where the default limit might cause a RecursionError.
    """
    if resource is None:
        return
    rec_limit = sys.getrecursionlimit()
    if rec_limit == limit:
        return
    try:
        resource.setrlimit(resource.RLIMIT_STACK, (limit, resource.RLIM_INFINITY))
        sys.setrecursionlimit(limit)
    except Exception as e:
        logger.error(f"Extending system recursive depth failed. {str(e)}")
        return e
    return limit


def generate_unique_id(obj: object):
    """
    Generate unique identify for objects
    :param obj: The object to generate the id for
    :return: string
    """
    pk = getattr(obj, "_id", None)
    if pk is None:
        pk = f"{obj.__class__.__name__}-{time.time()}-{str(uuid.uuid4())}"
        setattr(obj, "_id", pk)
    return pk


def build_event_arguments_from_pipeline(
    event_klass: typing.Type["EventBase"], pipeline: "Pipeline"
) -> typing.Tuple[typing.Dict[str, typing.Any], typing.Dict[str, typing.Any]]:
    """
    Builds the event arguments by extracting necessary data from the pipeline
    for a given event class.

    Args:
        event_klass: The class of the event (subclass of EventBase) for which
                     the arguments are being constructed.
        pipeline: The Pipeline object containing the data required to build
                  the event arguments.

    Returns:
        A tuple of two dictionaries:
            - The first dictionary contains the primary event arguments.
            - The second dictionary contains additional or optional event arguments.
    """
    return get_function_call_args(
        event_klass.__init__, pipeline
    ), get_function_call_args(event_klass.process, pipeline)


def get_function_call_args(
    func, params: typing.Union[typing.Dict[str, typing.Any], "Pipeline", object]
) -> typing.Dict[str, typing.Any]:
    """
    Extracts the arguments for a function call from the provided parameters.

    Args:
        func: The function for which arguments are to be extracted.
        params: A dictionary of parameters or a Pipeline object containing
                the necessary arguments for the function.

    Returns:
        A dictionary where the keys are the function argument names
        and the values are the corresponding argument values.
    """
    params_dict = {}
    try:
        sig = signature(func)
        for param in sig.parameters.values():
            if param.name != "self":
                value = (
                    params.get(param.name, param.default)
                    if isinstance(params, dict)
                    else getattr(params, param.name, param.default)
                )
                if value is not EMPTY and value is not Parameter.empty:
                    params_dict[param.name] = value
                else:
                    params_dict[param.name] = None
    except (ValueError, KeyError) as e:
        logger.warning(f"Parsing {func} for call parameters failed {str(e)}")

    for key in ["args", "kwargs"]:
        if key in params_dict and params_dict[key] is None:
            params_dict.pop(key, None)
    return params_dict


class AcquireReleaseLock(object):
    """A context manager for acquiring and releasing locks."""

    def __init__(self, lock):
        self.lock = lock

    def __enter__(self):
        self.lock.acquire()

    def __exit__(self, *args):
        self.lock.release()


def validate_batch_processor(batch_processor: BATCH_PROCESSOR_TYPE) -> bool:
    if not callable(batch_processor):
        raise ValueError(f"Batch processor '{batch_processor}' must be callable")

    sig = signature(batch_processor)
    if not sig.parameters or len(sig.parameters) != 2:
        raise ImproperlyConfigured(
            f"Batch processor '{batch_processor.__name__}' must have at least two arguments"
        )

    required_field_names = ["values", "batch_size", "chunk_size"]
    batch_kwarg = {}  # this is only use during the test

    for field_name, parameter in sig.parameters.items():
        if field_name == "chunk_size" or field_name == "batch_size":
            batch_kwarg[field_name] = 2
            if parameter.default is not Parameter.empty:
                if not isinstance(parameter.default, (int, float)):
                    raise ImproperlyConfigured(
                        f"Batch processor '{batch_processor.__name__}' argument 'batch_size/chunk_size' "
                        f"must have a default value type of int or float "
                    )
        if field_name not in required_field_names:
            raise ImproperlyConfigured(
                f"Batch processor '{batch_processor.__name__}' arguments must fields named {required_field_names}. "
                f"{field_name} cannot be use"
            )

    try:
        obj = batch_processor([1], **batch_kwarg)
        return (
            isinstance(obj, typing.Iterable)
            or isgeneratorfunction(obj)
            or isgenerator(obj)
        )
    except Exception as e:
        raise ImproperlyConfigured("Batch processor error") from e


def get_expected_args(
    func: typing.Callable, include_type: bool = False
) -> typing.Dict[str, typing.Any]:
    """
    Get the expected arguments of a function as a dictionary where the keys are argument names
    and the values are their default values (if any).

    Args:
        func (Callable): The function to inspect.
        include_type (bool): Whether the return type is expected.
    Returns:
        Dict[str, Any]: A dictionary with argument names as keys and default values (or `None` if no default) as values.
    """
    sig = signature(func)
    args_dict = {}

    for param_name, param in sig.parameters.items():
        if param.name == "self":
            continue
        if param.default is Parameter.empty:
            args_dict[param_name] = (
                param.annotation if include_type else Parameter.empty.__name__
            )
        else:
            args_dict[param_name] = param.annotation if include_type else param.default

    return args_dict


def get_obj_state(obj: typing.Any) -> typing.Dict[str, typing.Any]:
    try:
        return obj.get_state()
    except (AttributeError, NotImplementedError):
        return obj.__getstate__()


def get_obj_klass_import_str(obj: typing.Any) -> str:
    return f"{obj.__class__.__module__}.{obj.__class__.__qualname__}"


def send_data_over_socket(
    sock: socket.socket,
    data: bytes,
    chunk_size: typing.Optional[int] = None,
) -> int:
    """
    Send data over a socket connection in chunks.

    This function splits the given data into smaller chunks of the specified
    size and sends them over the provided client socket. It ensures that
    large data is sent efficiently without overwhelming the network connection.
    Args:
        sock (socket.socket): The socket object representing the
                                       active connection to the client.
        data (bytes): The data to be sent over the socket. It should be a bytes object.
        chunk_size (int): The maximum size (in bytes) for each chunk of data
                          to be sent in one transmission.
    Returns:
        int: The total number of bytes successfully sent across the socket.
    Raises:
        socket.error: If there is an error while sending data through the socket.
        TypeError: If the data provided is not serializable or the chunk_size
                   is non-positive.
    """
    now = time.time()
    # data = ForkingPickler.dumps(data, protocol=pickle.HIGHEST_PROTOCOL)
    # compressed_data = zlib.compress(data)
    data_size = len(data)
    sock.sendall(data_size.to_bytes(8, "big"))

    stream_fd = BytesIO(data)
    sent = 0

    if chunk_size is None:
        chunk = stream_fd.getvalue()
        sent = data_size
        sock.sendall(chunk)
    else:
        chunk_size = abs(chunk_size)
        while sent < data_size:
            chunk = stream_fd.read(chunk_size)
            if not chunk:
                break
            sock.sendall(chunk)
            sent += len(chunk)

    logger.debug(
        f"Successfully sent {data_size} bytes to {sock.getpeername()[0]} at {now} "
        f"and it took {time.time() - now:.2f} seconds"
    )

    return sent


def receive_data_from_socket(sock: socket.socket, chunk_size: int) -> bytes:
    """
    Receive data from a socket in chunks.
    Args:
        sock (socket.socket): The socket object from which data is to be
                               received. It must represent an active
                               connection.
        chunk_size (int): The size (in bytes) of each chunk to read at a time.
                          This allows for efficient handling of large data
                          transmissions.
    Returns:
        bytes: The complete data received from the socket, concatenated into
               a single bytes object.
    Raises:
        socket.error: If there is an error while receiving data from the socket.
        ValueError: If the received data is incomplete or the chunk size is
                    non-positive.
    """
    result_size = int.from_bytes(sock.recv(8), "big")
    result_data = b""
    while len(result_data) < result_size:
        chunk = sock.recv(min(chunk_size, result_size - len(result_data)))
        if not chunk:
            break
        result_data += chunk
    return result_data


def create_server_ssl_context(
    cert_path: str, key_path: str, ca_certs_path: str, require_client_cert: bool
) -> ssl.SSLContext:
    """
    Creates and configures an SSLContext object for secure communication.
    Args:
        cert_path (str): Path to the server's SSL certificate file.
        key_path (str): Path to the server's private key file.
        ca_certs_path (str): Path to the file containing CA certificates for verifying client certificates.
        require_client_cert (bool): Whether to require clients to present a valid certificate.
    Returns:
        ssl.SSLContext: A configured SSL context object ready for use in secure servers or sockets.
    """
    try:
        context = ssl.create_default_context(ssl.Purpose.CLIENT_AUTH)
        context.load_cert_chain(certfile=cert_path, keyfile=key_path)

        if ca_certs_path:
            context.load_verify_locations(ca_certs_path)
            if require_client_cert:
                context.verify_mode = ssl.CERT_REQUIRED

        return context
    except (ssl.SSLError, OSError) as e:
        logger.error(f"Failed to create SSL context: {str(e)}", exc_info=e)
        raise


def create_client_ssl_context(
    client_cert_path: str, client_key_path: str, ca_certs_path: str
) -> ssl.SSLContext:
    """
    Creates and configures an SSLContext object for secure communication.
    :param client_cert_path: Path to the client certificate file.
    :param client_key_path: Path to the client private key file.
    :param ca_certs_path: Path to the file containing CA certificates for verifying client certificates.
    :return: SSLContext object.
    """
    context = ssl.create_default_context(ssl.Purpose.SERVER_AUTH)

    if ca_certs_path:
        context.load_verify_locations(ca_certs_path)

    if client_cert_path and client_key_path:
        context.load_cert_chain(certfile=client_cert_path, keyfile=client_key_path)

    return context

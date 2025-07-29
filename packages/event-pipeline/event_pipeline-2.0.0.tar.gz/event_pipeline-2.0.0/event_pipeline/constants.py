import typing

PIPELINE_FIELDS = "__pipeline_fields__"

PIPELINE_STATE = "_state"

MAX_RETRIES = 5
MAX_BACKOFF_FACTOR = 0.05

#: Maximum backoff time.
MAX_BACKOFF = 100

UNKNOWN = object()


class EMPTY:
    pass


BATCH_PROCESSOR_TYPE = typing.Callable[
    [
        typing.Union[typing.Collection, typing.Any],
        typing.Optional[typing.Union[int, float]],
    ],
    typing.Union[typing.Iterator[typing.Any], typing.Generator],
]

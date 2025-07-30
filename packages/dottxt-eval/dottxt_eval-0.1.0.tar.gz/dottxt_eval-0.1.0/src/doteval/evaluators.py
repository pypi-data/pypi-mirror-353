import inspect

from doteval.metrics import Metric, accuracy
from doteval.models import Score


def evaluator(metrics: Metric | list[Metric]):
    if not isinstance(metrics, list):
        metrics = [metrics]

    def decorator(func):
        def wrapper(*args, **kwargs):
            value = func(*args, **kwargs)
            metadata = get_metadata(func, *args, **kwargs)
            return Score(func.__name__, value, metrics, metadata)

        wrapper.__name__ = func.__name__

        return wrapper

    return decorator


def get_metadata(func, *args, **kwargs):
    sig = inspect.signature(func)
    param_names = list(sig.parameters.keys())

    metadata = {}
    for i, arg in enumerate(args):
        if i < len(param_names):
            metadata[param_names[i]] = arg

    metadata.update(kwargs)

    return metadata


@evaluator(metrics=accuracy())
def exact_match(value, expected) -> bool:
    return value == expected

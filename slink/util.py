"""Utils"""
from dataclasses import dataclass
from typing import Union, Iterable, Iterator, Optional
from functools import partial


field_is_missing = type('field_is_missing', (), {})()


def _select_fields(d: dict, fields, handle_missing: Optional[str] = None, default=None):
    """Helper of select_fields; selects fields from a single dict,
    with control on what to do if the field is missing.

    >>> d = {'a': 1, 'b': 2, 'c': 3}
    >>> dict(_select_fields(d, ['c', 'a']))
    {'c': 3, 'a': 1}
    >>> dict(_select_fields(d, ['c', 'd', 'a'], handle_missing='default'))
    {'c': 3, 'd': None, 'a': 1}
    """
    if not handle_missing:
        for field in fields:
            yield field, d[field]
    elif handle_missing == 'skip':
        for field in fields:
            val = d.get(field, field_is_missing)
            if val is not field_is_missing:
                yield field, d[field]
    elif handle_missing == 'default':
        for field in fields:
            yield field, d.get(field, default)
    else:
        raise ValueError(f'Unknown handle_missing value')


def select_fields(
    iterable_of_dicts: Iterable[dict],
    fields,
    handle_missing: Optional[str] = None,
    default=None,
):
    """Get an iterable of "sub-dicts". That is, dicts with only specified fields.
    Further, the  order of the fields will be as specified in the `fields` argument.

    By default `handle_missing=False`; any missing fields will raise a KeyError.
    To fallback to a default in this case, set `handle_missing=False` and
    optionally specify the desired default.

    >>> iterable_of_dicts = [{'a': 1, 'b': 2, 'c': 3}, {'a': 10, 'b': 20}]
    >>> list(select_fields(iterable_of_dicts, fields=['c', 'a'], handle_missing='skip'))
    [{'c': 3, 'a': 1}, {'a': 10}]
    >>> list(select_fields(
    ... iterable_of_dicts, fields=['c', 'a'], handle_missing='default', default=999)
    ... )
    [{'c': 3, 'a': 1}, {'c': 999, 'a': 10}]
    """
    selector = partial(
        _select_fields, fields=fields, handle_missing=handle_missing, default=default
    )
    return map(dict, map(selector, iterable_of_dicts))


@dataclass
class GetFromIter:
    """From an iterat(or)(able), get a function that iteratively returns the next item.

    Might become deprecated in the future because a very slightly more
    convenient equivalent to doing "manually":

    ```
    partial(next, iterator)
    # or
    partial(next, iter(iterable))
    ```

    """

    iterator: Union[Iterable, Iterator]

    def __post_init__(self):
        if not isinstance(self.iterator, Iterator):
            self.iterator = iter(self.iterator)

    def __call__(self):
        return next(self.iterator)

"""Tools to make sequences"""

from itertools import accumulate
from functools import partial
from typing import Callable, Iterable, Optional, Union, Any
import random
import copy
from dataclasses import dataclass

from lined import CommandIter
from i2 import MultiFunc, Sig


def _call_from_dict(kwargs: dict, func: Callable, sig: Sig):
    """A i2.call_forgivingly optimized for our purpose

    The sig argument needs to be the Sig(func) to work correctly.
    """
    args, kwargs = sig.args_and_kwargs_from_kwargs(
        kwargs,
        allow_excess=True,
        ignore_kind=True,
        allow_partial=False,
        apply_defaults=True,
    )
    return func(*args, **kwargs)


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


class IterativeDictProcessing(MultiFunc):
    """Generate or transform a dict iteratively from a set of iterative rules (functions)

    This is useful when you need to generate dicts (or any other vector --
    i.e fixed-width schema-ed tuple/list/etc) that have correlated values.

    Deterministic example with specified input:

    >>> f = IterativeDictProcessing(
    ...     phase=lambda session: session * 10,
    ...     something_dependent=lambda session, phase: session + phase,
    ...     something_independent=lambda: 'hi'
    ... )
    >>> f({'session': 2})
    {'session': 2, 'phase': 20, 'something_dependent': 22, 'something_independent': 'hi'}

    Non-deterministic example with empty input.
    Here we demonstrate that the original input that seeds the iterative generation
    can be given by a function that will generate a random input.

    >>> import functools, random
    >>> f = IterativeDictProcessing(
    ...     session=functools.partial(random.uniform, 2, 9),
    ...     block=lambda session: session * 10,
    ...     something_dependent=lambda session, block: session + block,
    ...     something_independent=lambda: random.choice([True, False, None])
    ... )
    >>> # f() is equivalent to specifying empty dict; f({}); or factory; f(dict)
    >>> f()  # doctest: +SKIP
    {'session': 8.673108499155791, 'block': 86.7310849915579,
    'something_dependent': 95.4041934907137, 'something_independent': False}

    Note that, akin to working with a spreadsheet, sometimes you need to create
    intermediate variables to use in your formulas, but don't want those fields in
    your final data.
    To acheive this just filter out the unwanted fields.
    You can use `select_fields` for this.

    """

    def __init__(self, **unnamed_funcs):
        super().__init__(**unnamed_funcs)
        self.sigs = {name: Sig(func) for name, func in self.items()}

    def __call__(self, seed_dict=None, preproc=copy.copy):
        if seed_dict is None:
            seed_dict = dict()
        elif callable(seed_dict):
            seed_dict_factory = seed_dict
            seed_dict = seed_dict_factory()
        if preproc:  # should we
            seed_dict = preproc(seed_dict)
        assert isinstance(seed_dict, dict)
        for assign_to_name, func in self.items():
            seed_dict[assign_to_name] = _call_from_dict(
                seed_dict, func, self.sigs[assign_to_name]
            )
            # seed_dict[key] = call_forgivingly(func, **seed_dict)
        return seed_dict


def mk_copies(d, n_copies_field):
    n = d[n_copies_field]
    for _ in range(n):
        yield d.copy()


import itertools
from typing import Generator


def flatten_generators_recursively(x: Generator):
    for xi in x:
        if isinstance(xi, Generator):
            yield from flatten_generators_recursively(xi)
        else:
            yield xi


@dataclass
class Repeater:
    """Helper class to define the repetition of an object based on a fixed number or
    a number (unknown at the time of instantiation) that will be defined in a
    seed_dict"""

    n_repetitions: Union[int, str]

    def __call__(self, obj, seed_dict=None):
        if isinstance(self.n_repetitions, str):
            # if n_repetitions is a string, it's a field; get the number_of_repetitions
            n_repetitions = (seed_dict or {}).get(self.n_repetitions, None)
            if n_repetitions is None:
                raise KeyError(f'{self.n_repetitions} key not found in {seed_dict}')
        else:
            n_repetitions = self.n_repetitions
        return itertools.repeat(obj, n_repetitions)


@dataclass
class ReturnObj:
    obj: Any

    def __call__(self):
        return self.obj


def _prepare_formula_dict(formula_dict):
    for k, v in formula_dict.items():
        if not isinstance(v, Callable):
            yield k, ReturnObj(v)
        else:
            yield k, v


def _prepare_formulas(formulas):
    for i, formula in enumerate(formulas):
        if isinstance(formula, dict):
            yield from _prepare_formula_dict(formula)
        elif isinstance(formula, Repeater):
            yield f'repeater_{i}', formula
        elif isinstance(formula, (int, str)):
            yield f'repeater_{i}', Repeater(formula)
        else:
            raise TypeError(
                f'formulas should be dicts, Repeaters, ints or strings: ' f'{formula}'
            )


# Note: Doctests work in terminal but not in pycharm!
def dict_generator(*formulas):
    """helper function to make Expand objects.
    >>> from slink.sequences import Repeater
    >>> import itertools
    >>>
    >>> counter = itertools.count()
    >>> f = dict_generator(dict(
    ...     x=7,  # will be replaced with ReturnObj(y), an equivalent of lambda: 7
    ...     _1=Repeater(3),
    ...     y=lambda: next(counter),  # will return 0, then 1, then 2,...
    ...     z=lambda x, y: x * y),
    ... )
    >>> list(f())
    [{'x': 7, 'y': 0, 'z': 0}, {'x': 7, 'y': 1, 'z': 7}, {'x': 7, 'y': 2, 'z': 14}]
    >>>
    >>> counter = itertools.count()
    >>> f = dict_generator(dict(
    ...     x=7,  # will be replaced with ReturnObj(y), an equivalent of lambda: 7
    ...     _1=Repeater(3),
    ...     y=lambda: next(counter),  # will return 3, then 4, then 5,...
    ...     z=lambda x, y: x * y),
    ...     2  # will be replaced with Repeater(2)
    ... )
    >>> t = list(f())
    >>> t  # doctest: +NORMALIZE_WHITESPACE
    [{'x': 7, 'y': 0, 'z': 0}, {'x': 7, 'y': 0, 'z': 0},
    {'x': 7, 'y': 1, 'z': 7}, {'x': 7, 'y': 1, 'z': 7},
    {'x': 7, 'y': 2, 'z': 14}, {'x': 7, 'y': 2, 'z': 14}]

    Equivelently,

    >>> counter = itertools.count()
    >>> f = dict_generator(dict(
    ...     dict(x=7),
    ...     3,  # will be replaced with Repeater(3)
    ...     dict(y=lambda: next(counter), z=lambda x, y: x * y),
    ...     2  # will be replaced with Repeater(2)
    ... )
    >>> assert list(f())) == t
    """
    return Expand(**dict(_prepare_formulas(formulas)))


# Note: Doctests work in terminal but not in pycharm!
class Expand(MultiFunc):
    """Make objects that generate schemaed and formulaed dicts with repetition

    >>> from slink.sequences import Repeater
    >>> import itertools
    >>>
    >>> counter = itertools.count()
    >>> def count():
    ...     return next(counter)
    ...
    >>> f = Expand(
    ...     x=lambda: 7,
    ...     _1=Repeater(3),
    ... )
    >>> list(f())
    [{'x': 7}, {'x': 7}, {'x': 7}]
    >>>
    >>> f = Expand(
    ...     x=lambda: 7,
    ...     _1=Repeater(3),
    ...     y=lambda: next(counter),  # will return 0, then 1, then 2,...
    ... )
    >>> list(f())
    [{'x': 7, 'y': 0}, {'x': 7, 'y': 1}, {'x': 7, 'y': 2}]
    >>>
    >>>
    >>> f = Expand(
    ...     x=lambda: 7,
    ...     _1=Repeater(3),
    ...     y=lambda: next(counter),  # will return 3, then 4, then 5,....
    ...     z=lambda x, y: x * y,
    ... )
    >>> list(f())
    [{'x': 7, 'y': 3, 'z': 21}, {'x': 7, 'y': 4, 'z': 28}, {'x': 7, 'y': 5, 'z': 35}]
    >>>
    >>>
    >>> f = Expand(
    ...     x=lambda: 7,
    ...     _1=Repeater(3),
    ...     y=lambda: next(counter),  # will return 6, then 7, then 8,...
    ...     z=lambda x, y: x * y,
    ...     _2=Repeater(2)
    ... )
    >>> list(f())  # doctest: +NORMALIZE_WHITESPACE
    [{'x': 7, 'y': 6, 'z': 42}, {'x': 7, 'y': 6, 'z': 42},
    {'x': 7, 'y': 7, 'z': 49}, {'x': 7, 'y': 7, 'z': 49},
    {'x': 7, 'y': 8, 'z': 56}, {'x': 7, 'y': 8, 'z': 56}]
    """

    def __init__(self, **unnamed_funcs):
        super().__init__(**unnamed_funcs)
        self.sigs = {name: Sig(func) for name, func in self.items()}

    def __call__(self, seed_dict=None, preproc=copy.copy):
        # return map(next, self._all_calls(seed_dict, preproc))
        return flatten_generators_recursively(self._call_(seed_dict, preproc))

    def _call_(self, seed_dict=None, preproc=copy.copy):
        if seed_dict is None:
            seed_dict = dict()
        elif callable(seed_dict):
            seed_dict_factory = seed_dict
            seed_dict = seed_dict_factory()
        if preproc:  # should we
            seed_dict = preproc(seed_dict)
        # assert isinstance(seed_dict, dict)

        # get the first (name, func) pair
        if len(self) > 0:
            (name, func), *remaining = self.items()
            next_repeater = Expand(**dict(remaining))
            if isinstance(func, Repeater):
                repeater = func
                yield from map(next_repeater, repeater(seed_dict, seed_dict))
            else:
                seed_dict[name] = _call_from_dict(seed_dict, func, self.sigs[name])
                yield from next_repeater(seed_dict, preproc)
        else:
            yield seed_dict


# class TreeTraversalGeneration(MultiFunc):
#     def __init__(self, **unnamed_funcs):
#         super().__init__(**unnamed_funcs)
#         self.sigs = {name: Sig(func) for name, func in self.items()}
#
#     def __call__(self, seed_dict=None, preproc=copy.copy):
#         if seed_dict is None:
#             seed_dict = dict()
#         elif callable(seed_dict):
#             seed_dict_factory = seed_dict
#             seed_dict = seed_dict_factory()
#         if preproc:  # should we
#             seed_dict = preproc(seed_dict)
#         assert isinstance(seed_dict, dict)
#
#         for assign_to_name, func in self.items():
#             if isinstance(func, Expand):
#                 yield from func(seed_dict)
#             else:
#                 seed_dict[assign_to_name] = _call_from_dict(
#                     seed_dict, func, self.sigs[assign_to_name]
#                 )
#             # seed_dict[key] = call_forgivingly(func, **seed_dict)
#         yield seed_dict


def mk_monotone_sequence(delta_val_func=random.random, *args, start=0, **kwargs):
    """Make a monotone sequence of numbers by accumulating

    >>> from lined import Pipe
    >>> import itertools
    >>> get_slice = Pipe(itertools.islice, list)
    >>>
    >>> it = mk_monotone_sequence()
    >>> t = get_slice(it, 4)
    >>> assert len(t) == 4
    >>> assert t[0] == 0
    >>> t  # doctest: +SKIP
    [0, 0.522353704156762, 0.9681615026643958, 1.0927423253813298]
    >>> it = mk_monotone_sequence(random.uniform, 10, 100, start=7)
    >>> t = get_slice(it, 3)
    >>> assert len(t) == 3
    >>> assert t[0] == 7
    >>> t  # doctest: +SKIP
    [7, 62.808676729760556, 129.67231010126588]
    """
    return accumulate(CommandIter(delta_val_func, *args, **kwargs), initial=start)

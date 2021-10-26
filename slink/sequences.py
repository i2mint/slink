"""Tools to make sequences"""

from itertools import accumulate
from lined import CommandIter
import random
from i2 import call_forgivingly, MultiFunc


class IterativeDictProcessing(MultiFunc):
    """Generate or transform a dict from a set of dict-referential functions

    Deterministic example with specified input:

    >>> f = IterativeDictProcessing(
    ...     phase=lambda session: session * 10,
    ...     something_dependent=lambda session, phase: session + phase,
    ...     something_independent=lambda: 'hi'
    ... )
    >>> f({'session': 2})
    {'session': 2, 'phase': 20, 'something_dependent': 22, 'something_independent': 'hi'}

    Non-deterministic example with empty input

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

    """
    def __call__(self, seed_dict=None):
        if seed_dict is None:
            seed_dict = dict()
        elif callable(seed_dict):
            seed_dict_factory = seed_dict
            seed_dict = seed_dict_factory()
        assert isinstance(seed_dict, dict)
        for key, func in self.funcs.items():
            seed_dict[key] = call_forgivingly(func, **seed_dict)
        return seed_dict


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

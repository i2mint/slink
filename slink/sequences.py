"""Tools to make sequences"""

from itertools import accumulate
from lined import CommandIter
import random


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



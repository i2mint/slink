"""Slink: Sequence generator

Highlights:

>>> from slink import IterativeDictProcessing
>>> f = IterativeDictProcessing(
...     phase=lambda session: session * 10,
...     something_dependent=lambda session, phase: session + phase,
...     something_independent=lambda: 'hi'
... )
>>> f({'session': 2})
{'session': 2, 'phase': 20, 'something_dependent': 22, 'something_independent': 'hi'}

>>> from slink import dict_generator, Repeater
>>> import itertools
>>> counter = itertools.count()
>>> f = dict_generator(dict(
...     x=7,  # will be replaced with ReturnObj(y), an equivalent of lambda: 7
...     _1=Repeater(3),
...     y=lambda: next(counter),  # will return 0, then 1, then 2,...
...     z=lambda x, y: x * y),
...     1
... )
>>> list(f())
[{'x': 7, 'y': 0, 'z': 0}, {'x': 7, 'y': 1, 'z': 7}, {'x': 7, 'y': 2, 'z': 14}]


"""

from slink.seed_functions import (
    RandomCategoricalGenerator,
    RandomStringGenerator,
    RandomDictGenerator,
    RandomGenerator,
    rand_string,
)

from slink.sequences import (
    IterativeDictProcessing,
    Repeater,
    DictChain,
    dict_generator,
    mk_monotone_sequence,
)

from slink.util import (
    GetFromIter,
    select_fields,
)

# External tools that are useful to slink
from lined import CommandIter

"""Slink: Sequence generator"""

from slink.seed_functions import (
    RandomCategoricalGenerator,
    RandomStringGenerator,
    RandomDictGenerator,
    RandomGenerator
)

from slink.sequences import (
    IterativeDictProcessing,
    Repeater,
    DictChain,
    dict_generator,
    mk_monotone_sequence
)

from slink.util import (
    GetFromIter,
    select_fields,
)

# External tools that are useful to slink
from lined import CommandIter
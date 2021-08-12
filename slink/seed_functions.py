"""
Seed functions are the functions that produce the first sequence of the pipeline
of sequence transformations.

They're not the outer most layer:
The outer-most layer contains the whole pipeline,
and has as arguments any parameters that the steps of the pipeline might need.

A seed functions is called repeatedly to produce either an item at a time (`n=1`),
a chunk (`n>1`), or an iterable (`n=0`) that may or may not be a finite one. 
"""
from dataclasses import dataclass
from functools import partial
from typing import Callable, Union, Collection
from random import randint
import itertools

import numpy as np


@dataclass
class RandomCategoricalGenerator:
    """Generate categorical data in a controlled random way

    >>> r = RandomCategoricalGenerator()
    >>> it = r(None)
    >>> assert r() in r.categories # True or False
    >>> assert r(n=1) in r.categories # same as r()
    >>> result = r(n=3)
    >>> assert isinstance(result, list)  # e.g. [False, True, False]
    >>> r = RandomCategoricalGenerator(chunk_container=tuple)
    >>> result = r(n=3)
    >>> assert isinstance(result, tuple)  # e.g. (False, True, False)
    >>> result = itertools.islice(r(None), 0, 4)
    >>> assert set(result).issubset(r.categories)
    """

    categories: Collection = (True, False)
    chunk_container: Callable = list

    # TODO: Allow possibility of weighted categories (p argument of np.random.choice)
    # TODO: Being able to specify random seed

    def __post_init__(self):
        self.categories = np.array(
            list(self.categories)
        )  # make any iterable into a (sliceable) array
        self.n_categories = len(self.categories)

    def __call__(self, n: Union[int, None] = 1):
        """returns a single category by default, or a n-tuple if n > 1"""
        if n is not None:
            arr = np.random.choice(self.categories, n)
            if n == 1:
                return arr[0]
            else:
                return self.chunk_container(arr)
        else:
            generate_integers_forever = itertools.count()
            get_random_categories_index = partial(randint, 0, self.n_categories - 1)
            generate_categories_indices_forever = (
                get_random_categories_index() for _ in generate_integers_forever
            )
            return (self.categories[i] for i in generate_categories_indices_forever)


class RandomNumericalGenerator:
    """Generate numbers in a controlled random way"""


class RandomTupleGenerator:
    """Generate fixed-schema tuples (of numericals or tuples)
    Can be used to generate other fixed-schema objects (dict, custom classes, etc.)
    """

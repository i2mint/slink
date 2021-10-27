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
from typing import Callable, Union, Collection, Iterable, Tuple, Any, Dict, Sequence
from random import randint
import random
import itertools
import string
import abc

from lined import Command


class RandomGeneratorBase:
    chunk_container: Callable = list

    @abc.abstractmethod
    def generate_one(self):
        raise NotImplemented('Need to provide a generate_one method')

    def __call__(self, n=1):
        if n == 1:
            return self.generate_one()
        else:
            return self.chunk_container(self.read(n))

    def __iter__(self):
        while True:
            yield self()

    def read(self, n=1):
        return itertools.islice(self, n)


@dataclass
class RandomGenerator(RandomGeneratorBase):
    random_gen: Callable[[], Any]
    chunk_container: Callable = list

    def generate_one(self):
        return self.random_gen()


@dataclass
class RandomCategoricalGenerator(RandomGeneratorBase):
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

    categories: Sequence = (True, False)
    chunk_container: Callable = list

    # TODO: Allow possibility of weighted categories (p argument of np.random.choice)
    # TODO: Being able to specify random seed

    def __post_init__(self):
        self.categories = list(self.categories)  # make it sized
        self.n_categories = len(self.categories)

    def generate_one(self):
        return random.choice(self.categories)


def rand_string(str_size=(1, 9), alphabet=string.ascii_letters, joiner=''.join):
    if isinstance(str_size, (float, int)):
        str_size = (int(str_size), int(str_size))
    word_size = randint(*str_size)
    return joiner([random.choice(alphabet) for _ in range(word_size)])


@dataclass
class RandomStringGenerator(RandomGeneratorBase):
    """Random string generator

    >>> gen = RandomStringGenerator()
    >>> t = gen()
    >>> assert isinstance(t, str)
    >>> t  # doctest: +SKIP
    'CmwRB'
    >>> t = RandomStringGenerator(3, 'ab')(n=4)
    >>> t  # doctest: +SKIP
    ['bbb', 'bba', 'bab', 'abb']
    >>> assert all(isinstance(x, str) for x in t)
    >>> len(t)
    4
    """

    str_size: Union[int, Tuple[int, int]] = (1, 9)
    alphabet: Collection = string.ascii_letters
    joiner: Callable[[Iterable], str] = ''.join

    def __post_init__(self):
        if isinstance(self.str_size, (float, int)):
            self.str_size = (int(self.str_size), int(self.str_size))

    def generate_one(self):
        return rand_string(self.str_size, self.alphabet, self.joiner)


# TODO: Meant for postelizing random generators. Specify only a type, or enum etc.
DFLT_RAND_FUNC_FOR_TYPE = (
    (int, partial(random.randint, 0, 100)),
    (float, partial(random.uniform, 0, 100)),
    (str, partial(rand_string)),
)


ArglessFunc = Callable[[], Any]
GenForField = Union[Dict[str, ArglessFunc], Iterable[Tuple[str, ArglessFunc]]]


@dataclass
class RandomDictGenerator(RandomGeneratorBase):
    """Fixed-schema dict generator.

    >>> from lined import Command
    >>> rand_gen = RandomDictGenerator(gen_for_field=(
    ... ('rpm', Command(random.uniform, 100, 1000)),
    ... ('temperature', Command(random.randint, 15, 25)),
    ... ('id', Command(rand_string, str_size=(2, 5), alphabet='0123456789abcdef')),
    ... ('kind', RandomCategoricalGenerator(categories=[True, False, None]))
    ... ))
    >>> t = rand_gen()
    >>> t  # doctest: +SKIP
    {'rpm': 172.58455409094074, 'temperature': 21, 'id': '51a14', 'kind': True}
    >>> assert isinstance(t, dict)
    >>> assert list(t) == ['rpm', 'temperature', 'id', 'kind']

    You can also ask for several at once, by default, returned in a list.

    >>> rand_gen(3)  # doctest: +SKIP
    [{'rpm': 275.35599992556627, 'temperature': 21, 'id': '509', 'kind': True},
    {'rpm': 378.8770605317944, 'temperature': 23, 'id': '5657a', 'kind': None},
    {'rpm': 826.381460898361, 'temperature': 23, 'id': '4a53d', 'kind': False}]

    rand_gen is also an (infinite) iterable:

    >>> for x in rand_gen:
    ...     break
    >>> assert list(x) == ['rpm', 'temperature', 'id', 'kind']

    You can ask for an iterator with a limited number of elements.

    >>> it = rand_gen.read(3)
    >>> import itertools
    >>> assert isinstance(it, itertools.islice)
    >>> y = list(rand_gen.read(3))
    >>> assert len(y) == 3
    >>> assert list(y[0]) == ['rpm', 'temperature', 'id', 'kind']
    """

    gen_for_field: GenForField = (
        ('rpm', Command(random.uniform, 100, 1000)),
        ('temperature', Command(random.randint, 15, 25)),
        ('id', Command(rand_string, str_size=(2, 5), alphabet='0123456789abcdef')),
        ('kind', RandomCategoricalGenerator(categories=[True, False, None])),
    )
    chunk_container: Callable = list

    def __post_init__(self):
        self.gen_for_field = dict(self.gen_for_field)

    def generate_one(self):
        return {k: v() for k, v in self.gen_for_field.items()}


class RandomTupleGenerator(RandomDictGenerator):
    """Generate fixed-schema tuples (of numericals or tuples)
    Can be used to generate other fixed-schema objects (dict, custom classes, etc.)
    """

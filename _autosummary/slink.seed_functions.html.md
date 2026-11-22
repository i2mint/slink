# slink.seed_functions

Seed functions are the functions that produce the first sequence of the pipeline
of sequence transformations.

They’re not the outer most layer:
The outer-most layer contains the whole pipeline,
and has as arguments any parameters that the steps of the pipeline might need.

A seed functions is called repeatedly to produce either an item at a time (`n=1`),
a chunk (`n>1`), or an iterable (`n=0`) that may or may not be a finite one.

### Functions

| `rand_string`([str_size, alphabet, joiner])   |    |
|-----------------------------------------------|----|

### Classes

| [`RandomCategoricalGenerator`](#slink.seed_functions.RandomCategoricalGenerator)([categories, ...])    | Generate categorical data in a controlled random way                                                                                   |
|---------------------------------------------------------------------------------------------------|----------------------------------------------------------------------------------------------------------------------------------------|
| [`RandomDictGenerator`](#slink.seed_functions.RandomDictGenerator)([gen_for_field, ...])        | Fixed-schema dict generator.                                                                                                           |
| [`RandomGenerator`](#slink.seed_functions.RandomGenerator)(random_gen[, chunk_container])   |                                                                                                                                        |
| `RandomGeneratorBase`()                                                                           |                                                                                                                                        |
| [`RandomStringGenerator`](#slink.seed_functions.RandomStringGenerator)([str_size, alphabet, ...]) | Random string generator                                                                                                                |
| [`RandomTupleGenerator`](#slink.seed_functions.RandomTupleGenerator)([gen_for_field, ...])       | Generate fixed-schema tuples (of numericals or tuples) Can be used to generate other fixed-schema objects (dict, custom classes, etc.) |

### *class* slink.seed_functions.RandomCategoricalGenerator(categories=(True, False), chunk_container=<class 'list'>)

Bases: `RandomGeneratorBase`

Generate categorical data in a controlled random way

# TODO: See why this runs forever!!!
# >>> r = RandomCategoricalGenerator()
# >>> it = r(None)
# >>> assert r() in r.categories # True or False
# >>> assert r(n=1) in r.categories # same as r()
# >>> result = r(n=3)
# >>> assert isinstance(result, list)  # e.g. [False, True, False]
# >>> r = RandomCategoricalGenerator(chunk_container=tuple)
# >>> result = r(n=3)
# >>> assert isinstance(result, tuple)  # e.g. (False, True, False)
# >>> result = itertools.islice(r(None), 0, 4)
# >>> assert set(result).issubset(r.categories)

#### chunk_container

alias of [`list`](https://docs.python.org/3/builtins/stdtypes.html#list)

### *class* slink.seed_functions.RandomDictGenerator(gen_for_field=(('rpm', functools.partial(<bound method Random.uniform of <random.Random object>>, 100, 1000)), ('temperature', functools.partial(<bound method Random.randint of <random.Random object>>, 15, 25)), ('id', functools.partial(<function rand_string>, str_size=(2, 5), alphabet='0123456789abcdef')), ('kind', RandomCategoricalGenerator(categories=[True, False, None], chunk_container=<class 'list'>))), chunk_container=<class 'list'>)

Bases: `RandomGeneratorBase`

Fixed-schema dict generator.

#### NOTE
More power found in `slink` `IterativeDictProcessing` and `generate_dict`

`RandomDictGenerator` is left here because it has the common `RandomGeneratorBase`
interface.

```pycon
>>> from functools import partial
>>> rand_gen = RandomDictGenerator(gen_for_field=(
... ('rpm', partial(random.uniform, 100, 1000)),
... ('temperature', partial(random.randint, 15, 25)),
... ('id', partial(rand_string, str_size=(2, 5), alphabet='0123456789abcdef')),
... ('kind', RandomCategoricalGenerator(categories=[True, False, None]))
... ))
>>> t = rand_gen()
>>> t
{'rpm': 172.58455409094074, 'temperature': 21, 'id': '51a14', 'kind': True}
>>> assert isinstance(t, dict)
>>> assert list(t) == ['rpm', 'temperature', 'id', 'kind']
```

You can also ask for several at once, by default, returned in a list.

```pycon
>>> rand_gen(3)
[{'rpm': 275.35599992556627, 'temperature': 21, 'id': '509', 'kind': True},
{'rpm': 378.8770605317944, 'temperature': 23, 'id': '5657a', 'kind': None},
{'rpm': 826.381460898361, 'temperature': 23, 'id': '4a53d', 'kind': False}]
```

rand_gen is also an (infinite) iterable:

```pycon
>>> for x in rand_gen:
...     break
>>> assert list(x) == ['rpm', 'temperature', 'id', 'kind']
```

You can ask for an iterator with a limited number of elements.

```pycon
>>> it = rand_gen.read(3)
>>> import itertools
>>> assert isinstance(it, itertools.islice)
>>> y = list(rand_gen.read(3))
>>> assert len(y) == 3
>>> assert list(y[0]) == ['rpm', 'temperature', 'id', 'kind']
```

#### chunk_container

alias of [`list`](https://docs.python.org/3/builtins/stdtypes.html#list)

### *class* slink.seed_functions.RandomGenerator(random_gen, chunk_container=<class 'list'>)

Bases: `RandomGeneratorBase`

#### chunk_container

alias of [`list`](https://docs.python.org/3/builtins/stdtypes.html#list)

### *class* slink.seed_functions.RandomStringGenerator(str_size=(1, 9), alphabet='abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ', joiner=<built-in method join of str object>)

Bases: `RandomGeneratorBase`

Random string generator

```pycon
>>> gen = RandomStringGenerator()
>>> t = gen()
>>> assert isinstance(t, str)
>>> t
'CmwRB'
>>> t = RandomStringGenerator(3, 'ab')(n=4)
>>> t
['bbb', 'bba', 'bab', 'abb']
>>> assert all(isinstance(x, str) for x in t)
>>> len(t)
4
```

#### joiner(iterable,)

Concatenate any number of strings.

The string whose method is called is inserted in between each given string.
The result is returned as a new string.

### Example

‘.’.join([‘ab’, ‘pq’, ‘rs’]) -> ‘ab.pq.rs’

### *class* slink.seed_functions.RandomTupleGenerator(gen_for_field=(('rpm', functools.partial(<bound method Random.uniform of <random.Random object>>, 100, 1000)), ('temperature', functools.partial(<bound method Random.randint of <random.Random object>>, 15, 25)), ('id', functools.partial(<function rand_string>, str_size=(2, 5), alphabet='0123456789abcdef')), ('kind', RandomCategoricalGenerator(categories=[True, False, None], chunk_container=<class 'list'>))), chunk_container=<class 'list'>)

Bases: [`RandomDictGenerator`](#slink.seed_functions.RandomDictGenerator)

Generate fixed-schema tuples (of numericals or tuples)
Can be used to generate other fixed-schema objects (dict, custom classes, etc.)

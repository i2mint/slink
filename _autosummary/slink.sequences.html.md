# slink.sequences

Tools to make sequences

Highlights:

```pycon
>>> from slink.sequences import IterativeDictProcessing
>>> f = IterativeDictProcessing(
...     phase=lambda session: session * 10,
...     something_dependent=lambda session, phase: session + phase,
...     something_independent=lambda: 'hi'
... )
>>> f({'session': 2})
{'session': 2, 'phase': 20, 'something_dependent': 22, 'something_independent': 'hi'}
```

```pycon
>>> from slink.sequences import dict_generator, Repeater
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
```

### Functions

| [`call_repeatedly`](#slink.sequences.call_repeatedly)(func, \*args, \*\*kwargs)     |                                                                                   |
|------------------------------------------------------------------------------------------------|-----------------------------------------------------------------------------------|
| [`dict_generator`](#slink.sequences.dict_generator)(\*formulas)                    | helper function to make DictChain objects.                                        |
| `flatten_generators_recursively`(x)                                                            |                                                                                   |
| [`mk_monotone_sequence`](#slink.sequences.mk_monotone_sequence)([delta_val_func, start]) | Make a monotone sequence of numbers by accumulating random time durations/deltas. |
| `new_type`(name, typ[, doc])                                                                   |                                                                                   |

### Classes

| [`DictChain`](#slink.sequences.DictChain)(\*\*unnamed_funcs)             | Make objects that generate schemaed and formulaed dicts with repetition                                                                                           |
|-------------------------------------------------------------------------------------------|-------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| [`IterativeDictProcessing`](#slink.sequences.IterativeDictProcessing)(\*\*named_funcs) | Generate or transform a dict iteratively from a set of iterative rules (functions)                                                                                |
| [`Repeater`](#slink.sequences.Repeater)(n_repetitions)                  | Helper class to define the repetition of an object based on a fixed number or a number (unknown at the time of instantiation) that will be defined in a seed_dict |
| [`ReturnObj`](#slink.sequences.ReturnObj)(obj)                           |                                                                                                                                                                   |

### *class* slink.sequences.DictChain(\*\*unnamed_funcs)

Bases: `MultiFunc`

Make objects that generate schemaed and formulaed dicts with repetition

```pycon
>>> import itertools
>>>
>>> counter = itertools.count()
>>> def count():
...     return next(counter)
...
>>> f = DictChain(
...     x=lambda: 7,
...     _1=Repeater(3),
... )
>>> list(f())
[{'x': 7}, {'x': 7}, {'x': 7}]
>>>
>>> f = DictChain(
...     x=lambda: 7,
...     _1=Repeater(3),
...     y=lambda: next(counter),  # will return 0, then 1, then 2,...
... )
>>> list(f())
[{'x': 7, 'y': 0}, {'x': 7, 'y': 1}, {'x': 7, 'y': 2}]
>>>
>>>
>>> f = DictChain(
...     x=lambda: 7,
...     _1=Repeater(3),
...     y=lambda: next(counter),  # will return 3, then 4, then 5,....
...     z=lambda x, y: x * y,
... )
>>> list(f())
[{'x': 7, 'y': 3, 'z': 21}, {'x': 7, 'y': 4, 'z': 28}, {'x': 7, 'y': 5, 'z': 35}]
>>>
>>>
>>> f = DictChain(
...     x=lambda: 7,
...     _1=Repeater(3),
...     y=lambda: next(counter),  # will return 6, then 7, then 8,...
...     z=lambda x, y: x * y,
...     _2=Repeater(2)
... )
>>> list(f())
[{'x': 7, 'y': 6, 'z': 42}, {'x': 7, 'y': 6, 'z': 42},
{'x': 7, 'y': 7, 'z': 49}, {'x': 7, 'y': 7, 'z': 49},
{'x': 7, 'y': 8, 'z': 56}, {'x': 7, 'y': 8, 'z': 56}]
```

### *class* slink.sequences.IterativeDictProcessing(\*\*named_funcs)

Bases: `MultiFunc`

Generate or transform a dict iteratively from a set of iterative rules (functions)

This is useful when you need to generate dicts (or any other vector –
i.e fixed-width schema-ed tuple/list/etc) that have correlated values.

Deterministic example with specified input:

```pycon
>>> f = IterativeDictProcessing(
...     phase=lambda session: session * 10,
...     something_dependent=lambda session, phase: session + phase,
...     something_independent=lambda: 'hi'
... )
>>> f({'session': 2})
{'session': 2, 'phase': 20, 'something_dependent': 22, 'something_independent': 'hi'}
```

Non-deterministic example with empty input.
Here we demonstrate that the original input that seeds the iterative generation
can be given by a function that will generate a random input.

```pycon
>>> import functools, random
>>> f = IterativeDictProcessing(
...     session=functools.partial(random.uniform, 2, 9),
...     block=lambda session: session * 10,
...     something_dependent=lambda session, block: session + block,
...     something_independent=lambda: random.choice([True, False, None])
... )
>>> # f() is equivalent to specifying empty dict; f({}); or factory; f(dict)
>>> f()
{'session': 8.673108499155791, 'block': 86.7310849915579,
'something_dependent': 95.4041934907137, 'something_independent': False}
```

Note that, akin to working with a spreadsheet, sometimes you need to create
intermediate variables to use in your formulas, but don’t want those fields in
your final data.
To acheive this just filter out the unwanted fields.
You can use `slink.util.select_fields` for this.

### *class* slink.sequences.Repeater(n_repetitions)

Bases: [`object`](https://docs.python.org/3/builtins/functions.html#object)

Helper class to define the repetition of an object based on a fixed number or
a number (unknown at the time of instantiation) that will be defined in a
seed_dict

### *class* slink.sequences.ReturnObj(obj)

Bases: [`object`](https://docs.python.org/3/builtins/functions.html#object)

### slink.sequences.call_repeatedly(func, \*args, \*\*kwargs)

```pycon
>>> func = enumerate(range(4)).__next__
>>> iterator = call_repeatedly(func)
>>> list(iterator)
[(0, 0), (1, 1), (2, 2), (3, 3)]
```

* **Return type:**
  [`Iterator`](https://docs.python.org/3/library/collections.abc.html#collections.abc.Iterator)

### slink.sequences.dict_generator(\*formulas)

helper function to make DictChain objects.

```pycon
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
>>> t
[{'x': 7, 'y': 0, 'z': 0}, {'x': 7, 'y': 0, 'z': 0},
{'x': 7, 'y': 1, 'z': 7}, {'x': 7, 'y': 1, 'z': 7},
{'x': 7, 'y': 2, 'z': 14}, {'x': 7, 'y': 2, 'z': 14}]
```

Equivalently,

```pycon
>>> counter = itertools.count()
>>> f = dict_generator(
...     dict(x=7),
...     3,  # will be replaced with Repeater(3)
...     dict(y=lambda: next(counter), z=lambda x, y: x * y),
...     2  # will be replaced with Repeater(2)
... )
>>> assert list(f()) == t
```

### slink.sequences.mk_monotone_sequence(delta_val_func=<built-in method random of Random object>, \*args, start=0, \*\*kwargs)

Make a monotone sequence of numbers by accumulating random time durations/deltas.

```pycon
>>> from lined import Pipe
>>> import itertools
>>> get_slice = Pipe(itertools.islice, list)
>>>
>>> it = mk_monotone_sequence()
>>> t = get_slice(it, 4)
>>> assert len(t) == 4
>>> assert t[0] == 0
>>> t
[0, 0.522353704156762, 0.9681615026643958, 1.0927423253813298]
>>> it = mk_monotone_sequence(random.uniform, 10, 100, start=7)
>>> t = get_slice(it, 3)
>>> assert len(t) == 3
>>> assert t[0] == 7
>>> t
[7, 62.808676729760556, 129.67231010126588]
```

# slink.util

Utils

### Functions

| [`select_fields`](#slink.util.select_fields)(iterable_of_dicts, fields[, ...])   | Get an iterable of "sub-dicts".   |
|----------------------------------------------------------------------------------------------------|-----------------------------------|

### Classes

| [`GetFromIter`](#slink.util.GetFromIter)(iterator)   | From an iterat(or)(able), get a function that iteratively returns the next item.   |
|--------------------------------------------------------------------------|------------------------------------------------------------------------------------|

### *class* slink.util.GetFromIter(iterator)

Bases: [`object`](https://docs.python.org/3/builtins/functions.html#object)

From an iterat(or)(able), get a function that iteratively returns the next item.

Might become deprecated in the future because a very slightly more
convenient equivalent to doing “manually”:

```text
partial(next, iterator)
# or
partial(next, iter(iterable))
```

### slink.util.select_fields(iterable_of_dicts, fields, handle_missing=None, default=None)

Get an iterable of “sub-dicts”. That is, dicts with only specified fields.
Further, the  order of the fields will be as specified in the `fields` argument.

By default `handle_missing=False`; any missing fields will raise a KeyError.
To fallback to a default in this case, set `handle_missing=False` and
optionally specify the desired default.

```pycon
>>> iterable_of_dicts = [{'a': 1, 'b': 2, 'c': 3}, {'a': 10, 'b': 20}]
>>> list(select_fields(iterable_of_dicts, fields=['c', 'a'], handle_missing='skip'))
[{'c': 3, 'a': 1}, {'a': 10}]
>>> list(select_fields(
... iterable_of_dicts, fields=['c', 'a'], handle_missing='default', default=999)
... )
[{'c': 3, 'a': 1}, {'c': 999, 'a': 10}]
```

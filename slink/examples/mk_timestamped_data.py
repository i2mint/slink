"""Make timestamped data"""
from functools import partial
from creek import Creek
from lined import Line, LineParametrized, iterize


# ---------------------------------------------------------------------------------------
# Using creek to make a stream controlled by categoricals
"""
 a, b...  ──▶  wf_for(a), wf_for(b)...
"""
cat_map = {"a": [1, 2, 3], "b": [4, 5, 6]}
src = "aabbaab"


class CatCreek(Creek):
    def __init__(self, stream, cat_map):
        super().__init__(stream)
        self.cat_map = cat_map

    def data_to_obj(self, item):
        return self.cat_map[item]


class test_cat_creek:
    stream = CatCreek(stream=src, cat_map=cat_map)

    assert list(stream) == [
        [1, 2, 3],
        [1, 2, 3],
        [4, 5, 6],
        [4, 5, 6],
        [1, 2, 3],
        [1, 2, 3],
        [4, 5, 6],
    ]


# ---------------------------------------------------------------------------------------
# Composition of creeks using lined
"""
              ┌────────────┐
 cat_map  ──▶ │ TwCatCreek │ ──▶  output
              └────────────┘
                ▲
                │ stream
                │
              ┌────────────┐
 stream   ──▶ │  IdCreek   │
              └────────────┘
"""

# TW: Equivalent to just Creek
class IdCreek(Creek):
    def data_to_obj(self, item):
        return item


from lined import LineParametrized

pipe = LineParametrized(IdCreek, CatCreek)

assert list(pipe(src, cat_map=cat_map)) == [
    [1, 2, 3],
    [1, 2, 3],
    [4, 5, 6],
    [4, 5, 6],
    [1, 2, 3],
    [1, 2, 3],
    [4, 5, 6],
]


# ---------------------------------------------------------------------------------------
# analogue of iterize for creek

"""
 a, b...  ──▶  wf_for(a), wf_for(b)...  ──▶  transf_wf, transf_wf_b...
"""


# %%


def creek_iterize(f, stream):
    m = Creek(stream)
    m.data_to_obj = f
    return m


def func_to_creek(func):
    return partial(creek_iterize, func)


def test_func_to_creek():
    stream = [1, 2, 3]

    def double(item):
        return 2 * item

    assert list(func_to_creek(double)(stream)) == [2, 4, 6]

test_func_to_creek()

# ---------------------------------------------------------------------------------------
# Transform mapping into a function


def dict_to_func(d):
    return d.__getitem__


g = dict_to_func(cat_map)
assert g("a") == [1, 2, 3]


def dict_as_param(func):
    def g(d):
        return func(**d)

    return g


def test_dict_as_param():
    func = lambda x, y: x + y
    f = dict_as_param(func)
    assert f(dict(x=2, y=3)) == 5
    # but note that f isn't pickle-able

test_dict_as_param()


def test_func_to_creek_and_dict_to_func(cat_map=cat_map, src=src):
    stream = func_to_creek(dict_to_func(cat_map))(src)
    assert list(stream) == [
        [1, 2, 3],
        [1, 2, 3],
        [4, 5, 6],
        [4, 5, 6],
        [1, 2, 3],
        [1, 2, 3],
        [4, 5, 6],
    ]

test_func_to_creek_and_dict_to_func()



# TW: I stopped here
# ---------------------------------------------------------------------------------------
# Rewriting Christian's functions with creek

# %%

# Christian's initial function
def annot_timestamping(n_annot, start, end, wiggle=100):
    """
    Make synthetic timestamps
    """
    base = list(np.linspace(start, end, n_annot))
    wiggled = (
        base[0:1]
        + [i + np.random.randint(-wiggle, wiggle) for i in base[1:-1]]
        + base[-1:]
    )
    return wiggled



cat_lin_map = {
    "a": dict(start=1, stop=25, num=12),
    "b": dict(start=0, stop=5, num=30),
}

# %%

src = "aabbaab"
stream = Line(dict_to_func, func_to_creek)(cat_lin_map)(src)

# %%

list(stream)

# %%

import numpy as np

p = Line(dict_as_param, func_to_creek)(np.linspace)

# %%

list(p(stream))[:3]

# %%

dict_as_param(np.linspace)({"start": 1, "stop": 25, "num": 12})


# wiggle an array
def wiggle(arr, wig_factor):
    wiggling = np.random.randint(-wig_factor, wig_factor, len(arr))
    wiggling[0] = 0
    wiggling[-1] = 0

    return arr + wiggling


def wiggle_by(wig_factor):
    return partial(wiggle, wig_factor=wig_factor)


# ---------------------------------------------------------------------------------------
# package everything using lined


# symbols -> Iterable[dict] -> Iterable[np.array] - --(wiggle each array) --> Iterable[
#     np.array]


# This replaces the function annot_timestamping
src = "aabbaab"
p1 = Line(dict_to_func, func_to_creek)(cat_lin_map)
stream = p1(src)
p2 = Line(dict_as_param, func_to_creek)(np.linspace)
stream_final = p2(stream)
list(stream_final)[:3]

# %%

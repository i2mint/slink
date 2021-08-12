"""Examples and recipes"""


import itertools
from functools import partial

import numpy as np
from lined import iterize, Line, LineParametrized

# ---------------------------------------------------------------------------------------
# simple categorical map
cat_map = {"a": [1, 2, 3], "b": [4, 5, 6]}
get_list_for_cat = cat_map.__getitem__

# to make the sequence function from this item func, you can do:
iterized_get_list_for_cat = iterize(get_list_for_cat)
assert list(iterized_get_list_for_cat("abaa")) == [
    [1, 2, 3],
    [4, 5, 6],
    [1, 2, 3],
    [1, 2, 3],
]

# ---------------------------------------------------------------------------------------
# simple categorical map with seed generator
from slink.seed_functions import RandomCategoricalGenerator


def get_list_for_cat(category):
    return cat_map[category]


seed_gen = RandomCategoricalGenerator(categories="ab")

g = Line(seed_gen, iterize(get_list_for_cat), list, lambda x: x)
g(n=5)
# Example: [[4, 5, 6], [1, 2, 3], [1, 2, 3], [4, 5, 6], [4, 5, 6]]

# ---------------------------------------------------------------------------------------
# categorical seeds generating segments from normal distributions
cat_2_parms_map = {
    "a": dict(loc=5, scale=0.5, size=3),
    "b": dict(loc=10, scale=0.3, size=2),
}
get_params_for_cat = cat_2_parms_map.__getitem__
call_normal_rand_on_params = lambda params: np.random.normal(**params)

_cat_based_chunk_gen = Line(
    get_params_for_cat,  # get some params for a category
    call_normal_rand_on_params,  # draw from a normal distribution with those params
    iterize(int),  # cast the result to an int
    list,  # make the arrays into lists (because it's nicer for display)
)
cat_based_chunk_gen = iterize(_cat_based_chunk_gen)
list(cat_based_chunk_gen("abaa"))
# Example: [[4, 5, 5], [9, 10], [5, 4, 4], [4, 5, 4]]

# ---------------------------------------------------------------------------------------
# _cat_based_chunk_gen.dot_digraph() doesn't work in the above.
# To make that work, need to make get_params_for_cat a function with signature
def get_params_for_cat(category):
    return cat_2_parms_map[category]


def call_normal_rand_on_params(params):
    return np.random.normal(**params)


_cat_based_chunk_gen = Line(
    get_params_for_cat,  # get some params for a category
    call_normal_rand_on_params,  # draw from a normal distribution with those params
    iterize(int),  # cast the result to an int
    list,  # make the arrays into lists (because it's nicer for display)
)
cat_based_chunk_gen = iterize(_cat_based_chunk_gen)
list(cat_based_chunk_gen("abaa"))
# Example: [[4, 5, 4], [10, 9], [5, 5, 4], [5, 5, 5]]

# ---------------------------------------------------------------------------------------
# TODO: Replace norm_offset and norm_scale by a num normalizing function
# TODO: Give control over spectr normalization
def get_spectr_from_number(num, spectr, norm_offset, norm_scale):
    """
    This function is meant to be curried so that only num is left.
    - spectr is meant to be fixed for a given dimension of data (where the nums are
    coming from)
    -
    """
    spectr = np.array(spectr)
    normalized_num = (num - norm_offset) / norm_scale
    original_spectr_sum = sum(spectr)
    spectr = spectr + normalized_num  # shift spectr by normalized_num
    factor_to_conserve_sum = original_spectr_sum / sum(spectr)
    return spectr * factor_to_conserve_sum


list_of_ints = Line(
    iterize(int),
    list,
)

lists_of_list_of_ints = Line(
    iterize(list_of_ints),
    list,
)


_num_based_wf_gen = LineParametrized(
    (
        "get_spectr",
        partial(
            get_spectr_from_number, spectr=[400, 900, 50], norm_offset=2, norm_scale=10
        ),
    ),
    ("wf_to_spectr", np.fft.rfft),
    ("normalize_rfft", lambda rfft_wf: np.abs(rfft_wf)),
)

num_based_wf_gen = iterize(_num_based_wf_gen)
list_of_ints(_num_based_wf_gen(10000))
# Example: [1350, 229]

num_based_wf_gen = iterize(_num_based_wf_gen)
lists_of_list_of_ints(num_based_wf_gen([4, 10000, 70]))
# Example: [[1350, 739], [1350, 229], [1350, 728]]

# ---------------------------------------------------------------------------------------

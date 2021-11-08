import pytest
import functools, random
from i2 import Sig
from slink.sequences import (ReturnObj, _call_from_dict, IterativeDictProcessing,
                             Repeater, flatten_generators_recursively, ReturnObj,
                             _prepare_formula_dict, _prepare_formulas, dict_generator,
                             DictChain, mk_monotone_sequence
) 

def test_dummy():
    assert True

def test_call_from_dict():
    d = {'x':3, 'multiply_by':2, 'add_to':4}
    def func(x, multiply_by, add_to):
        return x*multiply_by + add_to
    s = Sig(func)
    result = _call_from_dict(d, func, s)
    expected = 10
    assert result == expected

def test_IterativeDictProcessing():
    f = IterativeDictProcessing(
         phase=lambda session: session * 10,
         something_dependent=lambda session, phase: session + phase,
         something_independent=lambda: 'hi'
    )
    assert f({'session': 2}) == {'session': 2, 'phase': 20, 
    'something_dependent': 22, 'something_independent': 'hi'}
    g = IterativeDictProcessing(
         session=functools.partial(random.uniform, 2, 9),
         block=lambda session: session * 10,
         something_dependent=lambda session, block: session + block,
         something_independent=lambda: random.choice([True, False, None])
    )
    result = g()
    assert result['something_dependent']==result['session']+result['block']

def test_Repeater():
    rep = Repeater(3)
    assert list(rep('hello'))==['hello','hello','hello']

def test_flatten_generators():
    def mk_gen(n):
        return (i*i for i in range(1,n))

    g=(mk_gen(i) for i in range(1,5))
    assert list(flatten_generators_recursively(g))==[1, 1, 4, 1, 4, 9]

def test_ReturnObj():
    t = ReturnObj('hey')
    assert t()=='hey'

def test_prepare_formula_dict():
    message = 'hey'
    d = {'key':message}
    d_prep = _prepare_formula_dict(d)
    for k,v in d_prep:
        assert v()==message

def test_prepare_formula_dict():
    formulas = [{'key':'word'}]
    for k,item in _prepare_formulas(formulas):
        assert ('key',item()) == ('key','word')

def test_dict_generator():
    import itertools
    counter = itertools.count()
    f = dict_generator(dict(
         x=7,  # will be replaced with ReturnObj(y), an equivalent of lambda: 7
         _1=Repeater(3),
         y=lambda: next(counter),  # will return 0, then 1, then 2,
         z=lambda x, y: x * y),
         1
    )
    assert list(f()) == [{'x': 7, 'y': 0, 'z': 0}, 
    {'x': 7, 'y': 1, 'z': 7}, {'x': 7, 'y': 2, 'z': 14}]

    counter = itertools.count()
    f = dict_generator(dict(
         x=7,  # will be replaced with ReturnObj(y), an equivalent of lambda: 7
         _1=Repeater(3),
         y=lambda: next(counter),  # will return 3, then 4, then 5,
         z=lambda x, y: x * y),
         2  # will be replaced with Repeater(2)
     )
    t = list(f())
    assert t  == [{'x': 7, 'y': 0, 'z': 0}, {'x': 7, 'y': 0, 'z': 0},
    {'x': 7, 'y': 1, 'z': 7}, {'x': 7, 'y': 1, 'z': 7},
    {'x': 7, 'y': 2, 'z': 14}, {'x': 7, 'y': 2, 'z': 14}]

def test_DictChain():
    import itertools
    counter = itertools.count()

    f = DictChain(
        x=lambda: 7,
        _1=Repeater(3),
    )
    assert list(f())==[{'x': 7}, {'x': 7}, {'x': 7}]
    f = DictChain(
        x=lambda: 7,
        _1=Repeater(3),
        y=lambda: next(counter),  # will return 0, then 1, then 2,    
    )
    assert list(f()) == [{'x': 7, 'y': 0}, {'x': 7, 'y': 1}, {'x': 7, 'y': 2}]
    f = DictChain(
        x=lambda: 7,
        _1=Repeater(3),
        y=lambda: next(counter),  # will return 3, then 4, then 5,
        z=lambda x, y: x * y,
    )
    assert list(f())== [{'x': 7, 'y': 3, 'z': 21}, {'x': 7, 'y': 4, 'z': 28}, {'x': 7, 'y': 5, 'z': 35}]
    f = DictChain(
        x=lambda: 7,
        _1=Repeater(3),
        y=lambda: next(counter),  # will return 6, then 7, then 8, 
        z=lambda x, y: x * y,
        _2=Repeater(2)
    )
    assert list(f()) == [{'x': 7, 'y': 6, 'z': 42}, {'x': 7, 'y': 6, 'z': 42},
    {'x': 7, 'y': 7, 'z': 49}, {'x': 7, 'y': 7, 'z': 49},
    {'x': 7, 'y': 8, 'z': 56}, {'x': 7, 'y': 8, 'z': 56}]

def test_mk_monotone_sequence():
    from lined import Pipe
    import itertools
    get_slice = Pipe(itertools.islice, list)
    
    def func(begin, end, start=0):
        return 42
    it = mk_monotone_sequence(func, 10, 100, start=7)
    t = get_slice(it, 3)
    assert len(t) == 3
    assert t == [7,49,91]
    
    
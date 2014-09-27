
import pytest
from fixedrec.layout import Layout
from fixedrec.utils import split_string, split_fields, n_, pset


def test_split_string():
    assert split_string('hello world') == ['hello world']
    assert split_string('hello world', 6) == ['hello ', 'world']


def test_split_fields():
    assert split_fields('hello big world', [5, None, 5]) == ['hello', ' big ', 'world']


def test_n_():
    assert n_(42) == 42
    assert n_('hello') == 'hello'
    assert n_('h\0llo') == 'h_llo'



def test_field():
    lout = Layout("=cH4s")
    assert len(lout) == 7
    assert lout.fields[0].size == 1
    assert lout.struct.size == len(lout)
    assert lout.split('a\0\0ABCD') == ['a', '\0\0', 'ABCD']
    print "LOUt:", str(lout)

    assert repr(lout) == '''{Layout(7) "=" [<Field: [0] "c" count=0 format='c' type="char" size=1>, <Field: [1] "H" count=0 format='H' type="unsigned short" size=2>, <Field: [2] "4s" count=4 format='s' type="char[]" size=4>]}'''

    assert str(lout) == """Layout for None: (len=7)
    @   0:#0                     c = 1
    @   1:#1                     H = 2
    @   3:#2                    4s = 4\n"""


def test_split_raises():
    lout = Layout("=4s")
    with pytest.raises(ValueError):
        lout.split('hello world')


def test_assignment():
    lout = Layout('=5si5s',
                  'greeting',
                  'answer',
                  'whom',
                  name="TestRec")
    lout.greeting = 'hello'
    assert lout.greeting == 'hello'

    lout.answer = 42
    assert lout.answer == 42

    lout.whom = 'world'
    assert lout.whom == 'world'


def test_prefix():
    lout = Layout('ci',
                  'chval',
                  'ival')
    assert lout.prefix == '@'
    lout.chval = 'X'
    lout.ival = 42
    data = bytearray(5)
    assert lout.fields[0].set_value(data, 'X') == 'X'
    assert data == 'X\0\0\0\0'

    assert lout.fields[1].set_value(data, 42) == 42
    assert data == 'X*\0\0\0'
    assert lout.fields[1].get_value(data) == 42


def test_nolayout():
    with pytest.raises(ValueError):
        Layout("")


def test_length():
    lout = Layout('=ci')
    assert len(lout) == 5

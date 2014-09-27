from fixedrec.rectypes import register_record, valid_rectype


def test_rectypes():

    @register_record
    class Foo:
        RECORD_LENGTH = 256
        RECTYPE = 'foo'
        layout = ' ' * RECORD_LENGTH

    assert valid_rectype('foo')
    assert not valid_rectype('bar')

# -*- coding: utf-8 -*-
import pytest
import textwrap
from fixedrec.record import Record
from fixedrec.utils import pset, pad, bsd_checksum
from fixedrec.layout import Layout
from fixedrec.rectypes import register_record, record_type


def test_pset():
    p = pset([('hello', 'world')])
    assert str(p) == textwrap.dedent("""\
    {
        hello: 'world'
    }""")

    assert repr(p) == "{hello: 'world'}"


record_layout = Layout(
    '=12x?3sQ16s16s68s128sHcc',
    'pad',
    'local',
    'rectype',
    'timestamp',
    'salt',
    'digest',
    'key',
    'data',
    'chksum',
    'cr',
    'nl',
    name="Record"
)

class MyBaseRecord(Record):
    def __init__(self, data=None, **kw):
        super(MyBaseRecord, self).__init__(record_layout, data, **kw)
        self.instance_var = 42


def test_pad():
    assert pad('foo', 4) == 'foo '
    assert pad('foo', 3) == 'foo'
    with pytest.raises(ValueError):
        assert pad('foo', 2)


def test_record_length():
    r = MyBaseRecord()
    print r
    length = len(r)
    print 'length:', length
    assert length == 256


def test_record_asdict():
    r = MyBaseRecord(key='hello')
    d = r.as_dict()
    assert d['local'] == '\0'
    assert d['key'].startswith('hello')


def test_lookup():
    r = MyBaseRecord(key='hello')
    assert r.key == 'hello'
    assert r.instance_var == 42


def test_example():
    @register_record
    class StatusRecord(Record):
        RECTYPE = 'ver'
        layout = Layout(
            '=4sQ10sH12xHcc',
            'rectype',
            'timestamp',
            'version',
            'reclen',
            'pad',
            'chksum',
            'cr',
            'nl',
            name="StatusRecord"
        )

        def __init__(self, data=None, **kw):
            super(StatusRecord, self).__init__(
                StatusRecord.layout, data, **kw)
            if data is None:
                self.rectype = StatusRecord.RECTYPE
                self.version = kw.get('version', '1.0.0')
                self.reclen = len(StatusRecord.layout)
                self.cr = b'\r'
                self.nl = b'\n'
            self.set_checksum()

        def set_checksum(self):
            "checksum of all preceeding fields."
            cksm_field = self._layout['chksum']
            cksm = bsd_checksum(self._data[:cksm_field.position])
            cksm_field.set_value(self._data, cksm)

    def verifyrec(srec):
        assert srec.version == '1.0.1'
        assert srec.timestamp == 0
        assert srec.reclen == 40
        assert srec.chksum == 39852

        parts = srec.pretty_parts()
        print 'parts:', parts
        assert parts[0] == 'ver_'  # field length is 4, _ is pretty for '\0'

        assert parts[2] == '1.0.1_____'
        assert parts[6] == '\r'
        assert parts[7] == '\n'

        assert record_type('ver') is StatusRecord
        return True

    r1 = StatusRecord(version='1.0.1')
    assert verifyrec(r1)
    
    r2 = StatusRecord(data=r1._data)
    assert verifyrec(r2)
    

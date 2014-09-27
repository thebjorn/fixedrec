import inspect
import os
import random
import string
import time
import pytest
from fixedrec import RecordFile, RecordFileError


DATADIR = os.path.join(os.path.split(__file__)[0], 'data') + '/blockfile-'


def fname(d):
    fn_name = inspect.currentframe().f_back.f_code.co_name
    return d / fn_name


def test_open(tmpdir):
    name = fname(tmpdir)
    ks = RecordFile(name, overwrite=True)
    assert len(ks) == 0
    assert os.stat(name.strpath).st_size == 0


def test_open_small_block(tmpdir):
    name = fname(tmpdir)
    with pytest.raises(RecordFileError):
        RecordFile(name, blocksize=1, overwrite=True)


def test_write(tmpdir):
    name = fname(tmpdir)
    bf = RecordFile(name, blocksize=4, overwrite=True)
    bf[-1] = 'aaaa'
    assert bf[0] == 'aaaa'


def test_repr(tmpdir):
    name = fname(tmpdir)
    fp = RecordFile(name, blocksize=4, overwrite=True)
    fp[-1] = 'aaaa'
    assert repr(fp) == 'aaaa'


def test_truncate(tmpdir):
    name = fname(tmpdir)
    fp = RecordFile(name, blocksize=4, overwrite=True)
    fp[-1] = 'aaaa'
    fp[-1] = 'bbbb'
    fp[-1] = 'cccc'
    fp.truncate(1)
    assert str(fp) == 'aaaa'


def test_goto_recnum_relative(tmpdir):
    name = fname(tmpdir)
    fp = RecordFile(name, blocksize=4, overwrite=True)
    fp[-1] = 'aaaa'
    fp[-1] = 'bbbb'
    fp[-1] = 'cccc'
    fp.goto_recnum(1)
    fp.goto_recnum_relative(1)
    assert fp.read() == 'cccc'
    fp.goto_recnum(1)
    fp.goto_recnum_relative(-1)
    assert fp.read() == 'aaaa'
    fp.goto_last_record()
    fp.goto_recnum_relative(-1)
    assert fp.read() == 'bbbb'


def test_swap(tmpdir):
    name = fname(tmpdir)
    fp = RecordFile(name, blocksize=4, overwrite=True)
    fp[-1] = 'aaaa'
    fp[-1] = 'bbbb'
    fp[-1] = 'cccc'
    fp.swap(0, 2)
    assert str(fp) == 'ccccbbbbaaaa'


def test_delete(tmpdir):
    name = fname(tmpdir)
    fp = RecordFile(name, blocksize=4, overwrite=True)
    fp[-1] = 'aaaa'
    fp[-1] = 'bbbb'
    fp[-1] = 'cccc'
    del fp[1]
    assert str(fp) == 'aaaacccc'


def test_read(tmpdir):
    name = fname(tmpdir)
    with RecordFile(name, blocksize=4, overwrite=True) as bf:
        bf[0] = 'aaaa'
        bf[1] = 'bbbb'
        bf[2] = 'cccc'
        bf[1] = 'xxxx'

    with RecordFile(name, blocksize=4) as b:
        assert b[0] == 'aaaa'
        assert b[1] == 'xxxx'
        assert b[2] == 'cccc'
        assert len(b) == 3

    with RecordFile(name, blocksize=4) as c:
        assert list(c) == ['aaaa', 'xxxx', 'cccc']


def test_open_missing_file(tmpdir):
    name = fname(tmpdir)
    bf = RecordFile(name)
    assert os.path.exists(name.strpath)


def test_out_of_bounds_write(tmpdir):
    name = fname(tmpdir)
    bf = RecordFile(name)
    bf[5] = 'abcd'
    assert bf[5] == 'abcd'
    assert len(bf) == 6


def test_err_blocksize(tmpdir):
    name = fname(tmpdir)
    with pytest.raises(RecordFileError) as e:
        bf = RecordFile(name, blocksize=4, overwrite=True)
        bf[-1] = 'a' * 5
    assert "didn't fit" in e.value.message


def test_err_no_filename():
    with pytest.raises(RecordFileError) as e:
        bf = RecordFile("")
    assert e.value.message == 'Missing file name.'


@pytest.mark.skipif("1")
def test_speed():  # pragma: no cover
    start = time.time()
    fname = DATADIR + 'test_speed'
    blocksize = 250
    records = 500
    randpos = [random.randrange(0, records) for _i in range(100000)]
    bf = RecordFile(fname, blocksize=blocksize)
    data = []
    for i in range(blocksize * records):
        data.append(random.choice(string.letters))
    data = ''.join(data)
    created = time.time()
    create_step = created - start
    assert create_step < 0.5

    for i in range(records):
        bf[i] = data[i * blocksize:(i + 1) * blocksize]
    filled = time.time()
    filled_step = filled - created
    assert filled_step < 0.02

    for i, p in enumerate(randpos[:10000]):
        n = i % records
        bf[p] = data[n * blocksize:(n + 1) * blocksize]
    writet = time.time()
    write_step = writet - filled
    assert write_step < 0.07  # 150K+ writes/sec

    for i, p in enumerate(randpos):
        v = bf[p]
    readt = time.time()
    read_step = readt - writet
    assert read_step < 0.55  # 180K+ reads/sec

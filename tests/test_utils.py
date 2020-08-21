def test_flags():
    from lona.utils import Flag

    flag = Flag(True)

    assert flag == True  # NOQA
    assert flag

    flag.set(False)

    assert flag == False  # NOQA
    assert not flag

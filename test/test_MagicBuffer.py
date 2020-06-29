from src.MagicBuffer import MagicBuffer


def test_magic_buffer_append_bs1():
    mb = MagicBuffer(buffer_size=1, max_count=16)
    k, v = mb.append('k1', '1')
    assert k == 'k1' and v == ('1',)


def test_magic_buffer_append_bs4():
    mb = MagicBuffer(buffer_size=4, max_count=8)
    k, v = mb.append('k1', '1')
    assert k is None and v is None
    k, v = mb.append('k1', '2')
    assert k is None and v is None
    k, v = mb.append('k1', '3')
    assert k is None and v is None
    k, v = mb.append('k1', '4')
    assert k == 'k1' and v == ('1', '2', '3', '4')

    # append multiple keys
    k, v = mb.append('k2', '1')
    k, v = mb.append('k1', '1')
    k, v = mb.append('k1', '2')
    k, v = mb.append('k1', '3')
    k, v = mb.append('k2', '2')
    assert k is None and v is None
    k, v = mb.append('k2', '3')
    assert k is None and v is None
    k, v = mb.append('k1', '4')
    assert k == 'k1' and v == ('1', '2', '3', '4')
    k, v = mb.append('k2', '4')
    assert k == 'k2' and v == ('1', '2', '3', '4')


def test_idle_key_must_be_dropped():
    mb = MagicBuffer(buffer_size=4, max_count=8)
    # Idle key should be removed
    k, v = mb.append('k0', '1')
    [mb.append('k_', '_') for i in range(0, 8)]
    k, v = mb.append('k0', '1')
    k, v = mb.append('k0', '2')
    k, v = mb.append('k0', '3')
    k, v = mb.append('k0', '4')
    assert k == 'k0' and v == ('1', '2', '3', '4')


def test_idle_key_must_be_revived():
    mb = MagicBuffer(buffer_size=4, max_count=8)
    # Idle key should be revived when new value inserted
    k, v = mb.append('k0', '1')
    [mb.append('k_', '_') for i in range(0, 7)]
    k, v = mb.append('k0', '2')
    [mb.append('k_', '_') for i in range(0, 7)]
    k, v = mb.append('k0', '3')
    [mb.append('k_', '_') for i in range(0, 7)]
    k, v = mb.append('k0', '4')
    assert k == 'k0' and v == ('1', '2', '3', '4')



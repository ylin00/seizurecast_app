import ast


def msg_encode(t:float, v:tuple):
    """encode t, v, into str.

    Args:
        t: time stamp in millisecond
        v: a list of float

    Returns:
        str: encoded string
    """
    return ("{'t':%.6f,'v':[" % float(t) + ','.join(map(str, v)) + "]}").encode('UTF-8')


def msg_decode(s):
    """decode msg into t and v."""
    mydata = ast.literal_eval(s.decode("UTF-8"))
    return mydata['t'], mydata['v']


if __name__ == '__main__':
    print(msg_encode(0, [1,2]))
    print(msg_decode(msg_encode(0, [1,2])))

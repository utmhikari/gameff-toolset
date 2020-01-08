import os


def get_iter_diff(a: iter, b: iter) -> (list, list, list):
    """
    get liter diff
    :param a: iterable a
    :param b: iterable b
    :return: a - b (removed), a ^ b (kept), b - a (added)
    """
    sa = set(a)
    sb = set(b)
    kp = set()
    rm = set()
    for aa in sa:
        if aa in sb:
            kp.add(aa)
            sb.remove(aa)
        else:
            rm.add(aa)
    rml = list(rm)
    kpl = list(kp)
    sbl = list(sb)
    rml.sort()
    kpl.sort()
    sbl.sort()
    return rml, kpl, sbl

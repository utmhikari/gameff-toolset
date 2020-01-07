import os


def get_list_diff(a: iter, b: iter) -> (list, list, list):
    """
    get list diff
    :param a: list a
    :param b: list b
    :return: a - b, a ^ b, b - a
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

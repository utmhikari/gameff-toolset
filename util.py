import os
import pprint

"""
Common utils
"""


def get_iter_diff(a: iter, b: iter) -> (list, list, list):
    """
    get liter diff
    :param a: iterable a
    :param b: iterable b
    :return: a - b (removed), a & b (kept), b - a (added)
    """
    sa = set(a)
    sb = set(b)
    rml = list(sa - sb)
    kpl = list(sa & sb)
    sbl = list(sb - sa)
    rml.sort()
    kpl.sort()
    sbl.sort()
    return rml, kpl, sbl


def lis(seq: []):
    """
    see https://stackoverflow.com/questions/3992697/longest-increasing-subsequence
    most similar to wiki
    :param seq: sequence list input
    :return: lis of seq
    """
    if not seq:
        return seq
    l = len(seq)
    if l <= 1:
        return seq
    m, p, k = [None] * l, [None] * l, 1
    m[0] = 0
    for i in range(1, l):
        # find the insert point (j) of seq[i] in current lis
        if seq[m[k - 1]] < seq[i]:
            j = k
        else:
            left, right = 0, k
            while right - left > 1:
                mid = (left + right) // 2
                if seq[m[mid - 1]] < seq[i]:
                    left = mid
                else:
                    right = mid
            j = left
        # m[j - 1]: smallest number's idx in seq on lis length of j
        # p[i]: prev lis number's idx
        # k: current lis length
        p[i] = m[j - 1]
        if j == k or seq[i] < seq[m[j]]:
            m[j] = i
            k = max(k, j + 1)
    pos = m[k - 1]
    ret = []
    for _ in range(k):
        ret.append(seq[pos])
        pos = p[pos]
    return ret[::-1]


def ppt(o):
    pprint.pprint(o, indent=2)


if __name__ == '__main__':
    print(lis([30, 10, 20, 50, 40, 80, 60]))

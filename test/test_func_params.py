# -*- coding: utf-8 -*-
"""Auto generated Google style docstrings.

Description
"""


def func(a, b, c=3, d=4, **kw):
    print("\noutput:\n")
    print(a, b, c, d, kw, end="\n")


def test():
    kw = {"test": 123, "ok": 321}
    func(1, 2, **kw)
    try:
        a = 1
        try:
            raise Exception
        except Exception:
            print(2)
            # return
            print(3)
            raise Exception
    except Exception:
        print(5)
        # return
    finally:
        print(1)
    print(4)

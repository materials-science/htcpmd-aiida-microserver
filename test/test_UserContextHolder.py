# -*- coding: utf-8 -*-
"""Example Google style docstrings.

Example module
"""
import threading
import time
from collections import Counter

from common import UserContextHolder

que = []


class Worker(threading.Thread):

    def run(self) -> None:
        super().run()

        UserContextHolder.set_username(self.name.split("-")[-1])
        time.sleep(3)
        UserContextHolder.set_login_user(user={"greeting": self.name})

        que.append(UserContextHolder.get_username())

        assert UserContextHolder.get_username() == self.name
        assert UserContextHolder.get_login_user().get("greeting") == self.name


def test():
    num = 15
    ws = []
    for i in range(0, num):
        w = Worker()
        w.start()
        ws.append(w)

    for w in ws:
        w.join()

    assert len(Counter(que).keys()) == num


if __name__ == '__main__':
    test()

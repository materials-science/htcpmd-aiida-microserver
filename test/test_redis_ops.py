import json
import unittest


class MyTestCase(unittest.TestCase):
    def test_something(self):
        # self.assertEqual(True, False)  # add assertion here
        from config import redis_client as redis
        redis.rpushx("test", json.dumps("[INFO] Have to dumps Str, or Java "
                                        "redis parser will report json parse "
                                        "error\n"))

        redis.rpush("test", json.dumps("[INFO] test rpush dumps json.\n"))

        print(redis.lrange("test", 0, -1), end="\n")

        print(redis.lrange("biz_job:38:logs", 0, -1), end="\n")


if __name__ == '__main__':
    unittest.main()

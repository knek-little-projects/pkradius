from concurrent.futures import ThreadPoolExecutor
from tornado.gen import coroutine as coro


class MainPool:
    pool = ThreadPoolExecutor(8)


def threadpool(f):
    def threaded_func(*args, **kwargs):
        return MainPool.pool.submit(f, *args, **kwargs)
    return threaded_func
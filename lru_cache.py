import time
from functools import update_wrapper


class _HashedSeq(list):

    __slots__ = 'hashvalue'

    def __init__(self, tup, hash=hash):
        self[:] = tup
        self.hashvalue = hash(tup)

    def __hash__(self):
        return self.hashvalue


def make_key(args, kwds,
             kwd_mark=(object(),),
             fasttypes={int, str, frozenset, type(None)},
             sorted=sorted, tuple=tuple, type=type, len=len):
    key = args
    if kwds:
        sorted_items = sorted(kwds.items())
        key += kwd_mark
        for item in sorted_items:
            key += item
    elif len(key) == 1 and type(key[0]) in fasttypes:
        return key[0]
    return _HashedSeq(key)


def lru_cache(maxsize=128):
    # Constants shared by all lru cache instances:
    PREV, NEXT, KEY, RESULT = 0, 1, 2, 3   # names for the link fields

    def decorating_function(user_function):

        cache = {}
        hits = misses = 0
        full = False
        root = []
        root[:] = [root, root, None, None]

        def wrapper(*args, **kwds):
            start_time = time.perf_counter()
            # Size limited caching that tracks accesses by recency
            nonlocal root, full
            key = make_key(args, kwds)
            link = cache.get(key)
            if link is not None:
                # Move the link to the front of the circular queue
                link_prev, link_next, _key, result = link
                link_prev[NEXT] = link_next
                link_next[PREV] = link_prev
                last = root[PREV]
                last[NEXT] = root[PREV] = link
                link[PREV] = last
                link[NEXT] = root
                print(
                    f"[Cache-Hit] {user_function.__name__}({args[0]}) ->{result}")
                return result
            result = user_function(*args, **kwds)
            if full:
                oldroot = root
                oldroot[KEY] = key
                oldroot[RESULT] = result

                root = oldroot[NEXT]
                oldkey = root[KEY]
                root[KEY] = root[RESULT] = None
                del cache[oldkey]
                cache[key] = oldroot
            else:
                last = root[PREV]
                link = [last, root, key, result]
                last[NEXT] = root[PREV] = cache[key] = link
                full = (len(cache) >= maxsize)
            end_time = time.perf_counter()
            print(
                f"{end_time-start_time:.8f}s {user_function.__name__}({args[0]}) ->{result}")
            return result

        def cache_clear(key):

            if(key in cache):
                del cache[key]
                nonlocal full
                full = False

        wrapper.cache_clear = cache_clear
        return update_wrapper(wrapper, user_function)

    return decorating_function

cache = {}
def memoize(n):
    if n not in cache:
        cache[n] = [0] * 10000  # large list
    return cache[n]
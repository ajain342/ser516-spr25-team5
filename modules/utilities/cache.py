from threading import Lock

class MetricCache:
    def __init__(self):
        self._cache = {}
        self._lock = Lock()

    def get(self, key):
        with self._lock:
            return self._cache.get(key)

    def add(self, key, value):
        with self._lock:
            self._cache[key] = value

    def contains(self, key):
        with self._lock:
            return key in self._cache

    def clear(self):
        with self._lock:
            self._cache.clear()

    def all(self):
        with self._lock:
            return dict(self._cache)

import time
import sys


def _monotonic_ns_fallback():
    return int(time.monotonic()*1e9)


if sys.version_info < (3, 7):
    monotonic_ns = _monotonic_ns_fallback

else:
    monotonic_ns = time.monotonic_ns

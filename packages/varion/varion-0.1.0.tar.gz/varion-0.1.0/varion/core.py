import numpy as np
from numba import njit

@njit
def xoshiro256starstar(seed, n):
    result = np.empty(n, dtype=np.uint64)
    s = np.array([seed, seed ^ 0xdeadbeef, seed >> 1, seed << 1], dtype=np.uint64)

    def rotl(x, k):
        return ((x << k) | (x >> (64 - k))) & ((1 << 64) - 1)

    for i in range(n):
        result[i] = rotl(s[1] * 5, 7) * 9
        t = s[1] << 17
        s[2] ^= s[0]
        s[3] ^= s[1]
        s[1] ^= s[2]
        s[0] ^= s[3]
        s[2] ^= t
        s[3] = rotl(s[3], 45)
    return result

def varion_random(seed=42, size=1000):
    raw = xoshiro256starstar(seed, size)
    return (raw % 1000000) / 1000000.0
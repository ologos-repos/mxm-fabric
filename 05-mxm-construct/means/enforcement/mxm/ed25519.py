"""Ed25519 signatures (RFC 8032), standard library only (ADR-MXK-0003).

The kernel only ever *verifies*; it holds public keys, never a signing secret. Signing is
here so an air-gapped Operator or Advisor can issue authorizations with the release alone;
any RFC 8032 implementation (OpenSSL, for one) produces interoperable signatures.

Verification rejects non-canonical encodings of R, the public key and the scalar
(S >= L), and rejects small-order R and public keys (the identity and the other points of
order dividing 8, which would otherwise verify signatures on arbitrary messages). It then
checks [S]B == R + [k]A. ``valid_public_key`` additionally requires the key to lie in the
prime-order subgroup; the kernel applies it to every trust-registry key when loading.

Limit: this is not constant-time. Verification handles no secrets, so that does not matter
to the kernel. Signing does handle one, so run it where no untrusted process can time it,
or sign with a constant-time implementation instead.
"""
from __future__ import annotations

import hashlib
from functools import lru_cache

P = 2**255 - 19
L = 2**252 + 27742317777372353535851937790883648493
D = -121665 * pow(121666, P - 2, P) % P
SQRT_M1 = pow(2, (P - 1) // 4, P)


def _recover_x(y: int, sign: int):
    if y >= P:
        return None
    x2 = (y * y - 1) * pow(D * y * y + 1, P - 2, P) % P
    if x2 == 0:
        return None if sign else 0
    x = pow(x2, (P + 3) // 8, P)
    if (x * x - x2) % P:
        x = x * SQRT_M1 % P
    if (x * x - x2) % P:
        return None
    if (x & 1) != sign:
        x = P - x
    return x


def _add(a, b):
    # Extended twisted Edwards coordinates (X, Y, Z, T), x = X/Z, y = Y/Z, xy = T/Z.
    aa = (a[1] - a[0]) * (b[1] - b[0]) % P
    bb = (a[1] + a[0]) * (b[1] + b[0]) % P
    cc = 2 * a[3] * b[3] * D % P
    dd = 2 * a[2] * b[2] % P
    e, f, g, h = bb - aa, dd - cc, dd + cc, bb + aa
    return (e * f % P, g * h % P, f * g % P, e * h % P)


def _mul(s: int, point):
    result = (0, 1, 1, 0)
    while s > 0:
        if s & 1:
            result = _add(result, point)
        point = _add(point, point)
        s >>= 1
    return result


def _equal(a, b) -> bool:
    return (a[0] * b[2] - b[0] * a[2]) % P == 0 and (a[1] * b[2] - b[1] * a[2]) % P == 0


_GY = 4 * pow(5, P - 2, P) % P
_GX = _recover_x(_GY, 0)
BASE = (_GX, _GY, 1, _GX * _GY % P)


def _is_identity(point) -> bool:
    return point[0] % P == 0 and (point[1] - point[2]) % P == 0


def _small_order(point) -> bool:
    return _is_identity(_mul(8, point))


def _compress(point) -> bytes:
    zinv = pow(point[2], P - 2, P)
    x, y = point[0] * zinv % P, point[1] * zinv % P
    return int.to_bytes(y | ((x & 1) << 255), 32, "little")


def _decompress(data: bytes):
    if len(data) != 32:
        return None
    y = int.from_bytes(data, "little")
    sign, y = y >> 255, y & ((1 << 255) - 1)
    x = _recover_x(y, sign)
    return None if x is None else (x, y, 1, x * y % P)


def _sha512_int(*parts: bytes) -> int:
    return int.from_bytes(hashlib.sha512(b"".join(parts)).digest(), "little")


def _expand(secret: bytes):
    if len(secret) != 32:
        raise ValueError("an Ed25519 secret key is 32 bytes")
    h = hashlib.sha512(secret).digest()
    a = int.from_bytes(h[:32], "little")
    a &= (1 << 254) - 8
    a |= 1 << 254
    return a, h[32:]


def valid_public_key(public: bytes) -> bool:
    """A canonical encoding of a point in the prime-order subgroup, of full order."""
    point = _decompress(public) if len(public) == 32 else None
    return point is not None and not _small_order(point) and _is_identity(_mul(L, point))


def public_key(secret: bytes) -> bytes:
    a, _ = _expand(secret)
    return _compress(_mul(a, BASE))


def sign(secret: bytes, message: bytes) -> bytes:
    a, prefix = _expand(secret)
    public = _compress(_mul(a, BASE))
    r = _sha512_int(prefix, message) % L
    big_r = _compress(_mul(r, BASE))
    s = (r + _sha512_int(big_r, public, message) * a) % L
    return big_r + int.to_bytes(s, 32, "little")


@lru_cache(maxsize=4096)
def verify(public: bytes, message: bytes, signature: bytes) -> bool:
    """True only for a valid signature. Pure, so results are memoized."""
    if len(public) != 32 or len(signature) != 64:
        return False
    a, r = _decompress(public), _decompress(signature[:32])
    if a is None or r is None or _small_order(a) or _small_order(r):
        return False
    s = int.from_bytes(signature[32:], "little")
    if s >= L:
        return False
    k = _sha512_int(signature[:32], public, message) % L
    return _equal(_mul(s, BASE), _add(r, _mul(k, a)))

"""Ed25519 (RFC 8032) as the kernel uses it: known answers, and a strict verifier."""
from __future__ import annotations

import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from mxm import ed25519 as E  # noqa: E402

# RFC 8032 §7.1, TEST 1-3: (secret key, public key, message, signature).
VECTORS = [
    ("9d61b19deffd5a60ba844af492ec2cc44449c5697b326919703bac031cae7f60",
     "d75a980182b10ab7d54bfed3c964073a0ee172f3daa62325af021a68f707511a", "",
     "e5564300c360ac729086e2cc806e828a84877f1eb8e5d974d873e065224901555fb8821590a33bacc61e39701cf9b46bd25bf5f0595bbe24655141438e7a100b"),
    ("4ccd089b28ff96da9db6c346ec114e0f5b8a319f35aba624da8cf6ed4fb8a6fb",
     "3d4017c3e843895a92b70aa74d1b7ebc9c982ccf2ec4968cc0cd55f12af4660c", "72",
     "92a009a9f0d4cab8720e820b5f642540a2b27b5416503f8fb3762223ebdb69da085ac1e43e15996e458f3613d0f11d8c387b2eaeb4302aeeb00d291612bb0c00"),
    ("c5aa8df43f9f837bedb7442f31dcb7b166d38535076f094b85ce3a2e0b4458f7",
     "fc51cd8e6218a1a38da47ed00230f0580816ed13ba3303ac5deb911548908025", "af82",
     "6291d657deec24024827e69c3abe01a30ce548a284743a445e3680d7db5ac3ac18ff9b538d16f290ae67f760984dc6594a7c15e9716ed28dc027beceea1ec40a"),
]


@pytest.mark.parametrize("secret, public, message, signature", VECTORS)
def test_rfc8032_known_answers(secret, public, message, signature):
    sk, pk, msg, sig = (bytes.fromhex(x) for x in (secret, public, message, signature))
    assert E.public_key(sk) == pk
    assert E.sign(sk, msg) == sig
    assert E.verify(pk, msg, sig)


def _vector():
    sk, pk, msg, sig = (bytes.fromhex(x) for x in VECTORS[2])
    return pk, msg, sig


def test_rejects_a_changed_message_or_signature():
    pk, msg, sig = _vector()
    assert not E.verify(pk, msg + b"\x00", sig)
    for i in (0, 31, 32, 63):
        bad = bytearray(sig); bad[i] ^= 1
        assert not E.verify(pk, msg, bytes(bad))


def test_rejects_the_malleable_s_plus_l_form():
    pk, msg, sig = _vector()
    s = int.from_bytes(sig[32:], "little")
    assert not E.verify(pk, msg, sig[:32] + int.to_bytes(s + E.L, 32, "little"))


def test_rejects_non_canonical_and_malformed_encodings():
    pk, msg, sig = _vector()
    non_canonical_y = int.to_bytes(E.P, 32, "little")
    assert not E.verify(non_canonical_y, msg, sig)
    assert not E.verify(pk, msg, non_canonical_y + sig[32:])
    assert not E.verify(pk[:31], msg, sig) and not E.verify(pk, msg, sig[:63])
    with pytest.raises(ValueError):
        E.sign(b"short", msg)


def test_a_signature_does_not_verify_under_another_key():
    other = E.public_key(bytes(range(32)))
    pk, msg, sig = _vector()
    assert not E.verify(other, msg, sig)


def _order(point):
    return next(n for n in (1, 2, 4, 8) if E._is_identity(E._mul(n, point)))


def _small_order_points():
    """One point of each order 1, 2, 4 and 8. [L]Q is pure torsion for any curve point Q."""
    for y in range(2, 1000):
        q = E._decompress(int.to_bytes(y, 32, "little"))
        if q is not None and _order(E._mul(E.L, q)) == 8:
            t8 = E._mul(E.L, q)
            break
    points = [E._mul(8, t8), E._mul(4, t8), E._mul(2, t8), t8]
    assert [_order(p) for p in points] == [1, 2, 4, 8]
    return points


def test_small_order_keys_and_nonces_never_verify():
    msg = b"anything at all"
    for point in _small_order_points():
        enc = E._compress(point)
        assert not E.verify(enc, msg, int.to_bytes(1, 32, "little") + bytes(32))
        assert not E.verify(enc, msg, enc + bytes(32))
        pk, _, sig = _vector()
        assert not E.verify(pk, msg, enc + sig[32:])
        assert not E.valid_public_key(enc)


def test_a_key_outside_the_prime_order_subgroup_is_not_a_valid_key():
    pk, _, _ = _vector()
    mixed = E._compress(E._add(E._decompress(pk), (0, E.P - 1, 1, 0)))
    assert E.valid_public_key(pk) and not E.valid_public_key(mixed)

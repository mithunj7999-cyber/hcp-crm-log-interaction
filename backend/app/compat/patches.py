"""
Runtime patches for environments where native DLLs are blocked
(e.g. Windows Application Control policies).

Must be imported before langchain / langgraph packages load.
"""

from __future__ import annotations

import hashlib
import os
import sys
import time
import types
from uuid import UUID


def _uuid7(timestamp: int | None = None, nanos: int | None = None) -> UUID:
    """Pure-Python UUIDv7 fallback compatible with uuid_utils.compat.uuid7."""
    if timestamp is None:
        unix_ts_ms = int(time.time() * 1000)
    else:
        unix_ts_ms = timestamp * 1000
        if nanos is not None:
            unix_ts_ms += nanos // 1_000_000

    rand_a = int.from_bytes(os.urandom(2), "big") & 0x0FFF
    rand_b = int.from_bytes(os.urandom(8), "big") & 0x3FFFFFFFFFFFFFFF

    uuid_int = (unix_ts_ms & 0xFFFFFFFFFFFF) << 80
    uuid_int |= 0x7 << 76
    uuid_int |= rand_a << 64
    uuid_int |= 0x2 << 62
    uuid_int |= rand_b
    return UUID(int=uuid_int)


def apply_uuid_utils_patch() -> None:
    """Register a pure-Python uuid_utils shim before the real package loads."""
    if "uuid_utils" in sys.modules:
        return

    compat = types.ModuleType("uuid_utils.compat")
    compat.uuid7 = _uuid7

    uuid_utils = types.ModuleType("uuid_utils")
    uuid_utils.compat = compat
    uuid_utils.__version__ = "0.0.0-pure"

    sys.modules["uuid_utils.compat"] = compat
    sys.modules["uuid_utils"] = uuid_utils


class _XXH3_128:
    """Minimal xxh3_128 stand-in backed by blake2b."""

    def __init__(self, data: bytes | str) -> None:
        if isinstance(data, str):
            data = data.encode()
        self._digest = hashlib.blake2b(data, digest_size=16).digest()

    def digest(self) -> bytes:
        return self._digest

    def hexdigest(self) -> str:
        return self._digest.hex()


def _xxh3_128_hexdigest(data: bytes | str) -> str:
    if isinstance(data, str):
        data = data.encode()
    return hashlib.blake2b(data, digest_size=16).hexdigest()


def apply_xxhash_patch() -> None:
    """Register a pure-Python xxhash shim before langgraph/langsmith import it."""
    if "xxhash" in sys.modules:
        return

    xxhash = types.ModuleType("xxhash")
    xxhash.xxh3_128 = _XXH3_128
    xxhash.xxh3_128_hexdigest = _xxh3_128_hexdigest
    xxhash.__version__ = "0.0.0-pure"

    sys.modules["xxhash"] = xxhash


def apply_native_dependency_patches() -> None:
    apply_uuid_utils_patch()
    apply_xxhash_patch()


apply_native_dependency_patches()

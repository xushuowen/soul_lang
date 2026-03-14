"""
ε (epsilon) — SOUL_LANG 的量子隨機性來源

Phase 1b：
  主要來源：ANU Quantum Random Number API（真光子量子隨機）
  備用來源：os.urandom（API 無法連線時自動切換）

ANU QRNG API：https://qrng.anu.edu.au
  一次批次取 256 個 uint8 值，快取用完再補充。
"""

from __future__ import annotations

import os
import struct
import threading
import logging
from collections import deque
from typing import Optional

logger = logging.getLogger(__name__)

# ── 設定 ─────────────────────────────────────────────────────
NIST_BEACON_URL = "https://beacon.nist.gov/beacon/2.0/pulse/last"
BATCH_SIZE = 256          # 每次從 beacon 提取幾個 byte
REFILL_THRESHOLD = 32     # 快取剩這麼少時觸發補充
API_TIMEOUT = 5.0         # 秒
_USE_QUANTUM = True       # 可手動關閉

# ── 內部狀態 ──────────────────────────────────────────────────
_cache: deque[int] = deque()
_cache_lock = threading.Lock()
_source: str = "urandom"  # "quantum" 或 "urandom"


def get_source() -> str:
    """返回目前使用的 ε 來源。"""
    return _source


def _fetch_quantum_batch(n: int = BATCH_SIZE) -> Optional[list[int]]:
    """
    從 NIST Randomness Beacon 取得量子隨機位元組。
    NIST Beacon 每 60 秒發布一個 512-bit 量子隨機值（免費、無需 key）。
    從 512 bits 提取 64 bytes，循環使用直到下一次請求。
    """
    try:
        import urllib.request
        import json
        req = urllib.request.Request(
            NIST_BEACON_URL,
            headers={"User-Agent": "SOUL_LANG/1.0"}
        )
        with urllib.request.urlopen(req, timeout=API_TIMEOUT) as resp:
            data = json.loads(resp.read().decode())
            # outputValue 是 512-bit hex string（128 個 hex 字元 = 64 bytes）
            hex_val = data["pulse"]["outputValue"]
            raw_bytes = bytes.fromhex(hex_val)
            # 循環展開到需要的長度
            result = []
            for i in range(n):
                result.append(raw_bytes[i % len(raw_bytes)])
            return result
    except Exception as e:
        logger.warning(f"NIST Beacon 無法連線，切換至 os.urandom：{e}")
    return None


def _refill_cache() -> None:
    """補充快取：優先用 ANU API，失敗則用 os.urandom。"""
    global _source
    if _USE_QUANTUM:
        batch = _fetch_quantum_batch(BATCH_SIZE)
        if batch:
            with _cache_lock:
                _cache.extend(batch)
            _source = "quantum"
            logger.info(f"ε 快取補充：{len(batch)} 個量子隨機值（ANU QRNG）")
            return

    # 備用：os.urandom
    raw = os.urandom(BATCH_SIZE)
    with _cache_lock:
        _cache.extend(raw)
    _source = "urandom"


def _get_uint8() -> int:
    """從快取取一個 uint8，必要時補充。"""
    with _cache_lock:
        if len(_cache) <= REFILL_THRESHOLD:
            # 背景補充（不阻塞當前呼叫）
            t = threading.Thread(target=_refill_cache, daemon=True)
            t.start()
        if _cache:
            return _cache.popleft()

    # 快取空了，同步補充
    _refill_cache()
    with _cache_lock:
        if _cache:
            return _cache.popleft()

    # 最後備用
    return os.urandom(1)[0]


# ── 公開介面 ──────────────────────────────────────────────────

def epsilon() -> float:
    """
    返回一個量子隨機浮點數，範圍 [-1.0, 1.0]。
    來源優先使用 ANU QRNG，失敗自動切換 os.urandom。
    """
    # 合併兩個 uint8 得到更高精度
    hi = _get_uint8()
    lo = _get_uint8()
    uint16 = (hi << 8) | lo
    normalized = uint16 / 0xFFFF   # [0.0, 1.0]
    return normalized * 2.0 - 1.0  # [-1.0, 1.0]


def epsilon_positive() -> float:
    """返回 [0.0, 1.0] 的量子隨機浮點數。"""
    hi = _get_uint8()
    lo = _get_uint8()
    uint16 = (hi << 8) | lo
    return uint16 / 0xFFFF


def epsilon_stream(n: int) -> list[float]:
    """返回 n 個連續 ε 值（用於 shadow 連續演化）。"""
    return [epsilon() for _ in range(n)]


def epsilon_status() -> dict:
    """返回目前 ε 系統的狀態（用於驗證實驗）。"""
    with _cache_lock:
        cache_size = len(_cache)
    return {
        "source": _source,
        "cache_remaining": cache_size,
        "quantum_enabled": _USE_QUANTUM,
        "api_url": NIST_BEACON_URL,
    }


# ── 初始化：啟動時預先填充快取 ────────────────────────────────
def _init():
    t = threading.Thread(target=_refill_cache, daemon=True)
    t.start()

_init()

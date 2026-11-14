from collections.abc import Sequence
from dataclasses import dataclass

from download_speed.fetch import FetchResult

BITS_PER_BYTE: int = 8
MEGA: int = 1_000_000


@dataclass(frozen=True, slots=True)
class Stats:
    count: int
    total_bytes: int
    total_s: float
    mean_s: float
    mbit_per_s: float
    mbyte_per_s: float


def summarize(results: Sequence[FetchResult]) -> Stats:
    if not results:
        raise ValueError("no results to summarize")

    count: int = len(results)
    total_bytes: int = sum(result.size_bytes for result in results)
    total_s: float = sum(result.elapsed_s for result in results)

    if total_s <= 0:
        raise ValueError(f"total time must be positive, got {total_s}")

    bytes_per_s: float = total_bytes / total_s

    return Stats(
        count=count,
        total_bytes=total_bytes,
        total_s=total_s,
        mean_s=total_s / count,
        mbit_per_s=bytes_per_s * BITS_PER_BYTE / MEGA,
        mbyte_per_s=bytes_per_s / MEGA,
    )

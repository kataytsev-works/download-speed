import http.client
import time
import urllib.error
import urllib.request
from collections.abc import Iterator
from dataclasses import dataclass
from typing import Final

from download_speed import DIST_NAME, __version__

CHUNK_SIZE: int = 64 * 1024

REQUEST_HEADERS: Final[dict[str, str]] = {
    "User-Agent": f"{DIST_NAME}/{__version__}",
    "Accept-Encoding": "identity",
    "Cache-Control": "no-cache",
}


@dataclass(frozen=True, slots=True)
class FetchResult:
    size_bytes: int
    elapsed_s: float


class FetchError(Exception):
    pass


def fetch(url: str, *, timeout: float) -> FetchResult:
    request = urllib.request.Request(url=url, headers=REQUEST_HEADERS)

    time_start = time.perf_counter()

    try:
        with urllib.request.urlopen(request, timeout=timeout) as response:
            size_bytes = 0
            while True:
                chunk = response.read(CHUNK_SIZE)

                if not chunk:
                    break

                size_bytes += len(chunk)

            if response.length:
                raise FetchError(f"{url}: connection closed, {response.length} bytes missing")
    except urllib.error.HTTPError as exc:
        exc.close()
        raise FetchError(f"{url}: HTTP {exc.code} {exc.reason}") from exc
    except urllib.error.URLError as exc:
        raise FetchError(f"{url}: {exc.reason}") from exc
    except TimeoutError as exc:
        raise FetchError(f"{url}: timed out after {timeout} s") from exc
    except http.client.HTTPException as exc:
        raise FetchError(f"{url}: broken response: {exc!r}") from exc
    except OSError as exc:
        raise FetchError(f"{url}: connection error: {exc}") from exc

    time_end = time.perf_counter()

    execution_time = time_end - time_start
    return FetchResult(size_bytes=size_bytes, elapsed_s=execution_time)


def measure(url: str, *, count: int, timeout: float) -> Iterator[FetchResult]:
    for _ in range(count):
        yield fetch(url, timeout=timeout)

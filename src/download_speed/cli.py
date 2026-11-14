import argparse
import math
import sys
import urllib.parse
from collections.abc import Sequence

from download_speed import DIST_NAME, __version__
from download_speed.fetch import FetchError, FetchResult, measure
from download_speed.stats import MEGA, Stats, summarize

ALLOWED_SCHEMES: frozenset[str] = frozenset({"http", "https"})
DEFAULT_COUNT: int = 10
DEFAULT_TIMEOUT_S: float = 30.0
EXIT_OK: int = 0
EXIT_FETCH_ERROR: int = 1
EXIT_INTERRUPTED: int = 130


def http_url(value: str) -> str:
    parts: urllib.parse.SplitResult = urllib.parse.urlsplit(value)
    if parts.scheme not in ALLOWED_SCHEMES or not parts.hostname:
        raise argparse.ArgumentTypeError(f"expected an http(s) URL with a host, got {value!r}")
    return value


def positive_int(value: str) -> int:
    try:
        number: int = int(value)
    except ValueError:
        raise argparse.ArgumentTypeError(f"expected an integer, got {value!r}") from None
    if number <= 0:
        raise argparse.ArgumentTypeError(f"expected a positive integer, got {number}")
    return number


def positive_float(value: str) -> float:
    try:
        number: float = float(value)
    except ValueError:
        raise argparse.ArgumentTypeError(f"expected a number, got {value!r}") from None
    if not math.isfinite(number) or number <= 0:
        raise argparse.ArgumentTypeError(f"expected a positive finite number, got {value!r}")
    return number


def build_parser() -> argparse.ArgumentParser:
    parser: argparse.ArgumentParser = argparse.ArgumentParser(
        prog=DIST_NAME,
        description=(
            "Download a URL several times in a row and report the average request time, "
            "the total amount downloaded and the download speed."
        ),
        epilog=(
            "Units: speed in Mbit/s and MB/s, volume in MB, with decimal prefixes "
            "(1 MB = 10^6 bytes, 1 Mbit = 10^6 bits)."
        ),
    )
    parser.add_argument("url", type=http_url, help="http(s) URL to download")
    parser.add_argument(
        "-n",
        "--count",
        type=positive_int,
        default=DEFAULT_COUNT,
        help=f"number of sequential requests (default: {DEFAULT_COUNT})",
    )
    parser.add_argument(
        "-t",
        "--timeout",
        type=positive_float,
        default=DEFAULT_TIMEOUT_S,
        help=f"socket timeout per operation, seconds (default: {DEFAULT_TIMEOUT_S:g})",
    )
    parser.add_argument("--version", action="version", version=f"%(prog)s {__version__}")
    return parser


def format_result(index: int, total: int, result: FetchResult) -> str:
    return f"[{index}/{total}] {result.size_bytes} bytes in {result.elapsed_s:.3f} s"


def format_stats(stats: Stats) -> str:
    total_mb: float = stats.total_bytes / MEGA
    lines: list[str] = [
        f"Requests:         {stats.count}",
        f"Total downloaded: {total_mb:.2f} MB ({stats.total_bytes} bytes)",
        f"Average time:     {stats.mean_s:.3f} s",
        f"Speed:            {stats.mbit_per_s:.2f} Mbit/s ({stats.mbyte_per_s:.2f} MB/s)",
    ]
    return "\n".join(lines)


def main(argv: Sequence[str] | None = None) -> int:
    args: argparse.Namespace = build_parser().parse_args(argv)
    url: str = args.url
    count: int = args.count
    timeout: float = args.timeout

    results: list[FetchResult] = []
    try:
        for index, result in enumerate(measure(url, count=count, timeout=timeout), start=1):
            results.append(result)
            print(format_result(index, count, result), flush=True)
    except FetchError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return EXIT_FETCH_ERROR
    except KeyboardInterrupt:
        print("interrupted", file=sys.stderr)
        return EXIT_INTERRUPTED

    print(format_stats(summarize(results)))
    return EXIT_OK

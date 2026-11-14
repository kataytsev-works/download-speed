# download-speed

Measure how fast a URL downloads. `download-speed` fetches the URL several times in a row, reads every
response to the end, and reports the average request time, the total size and the speed.

```
$ download-speed https://proof.ovh.net/files/10Mb.dat
[1/10] 10485760 bytes in 0.711 s
[2/10] 10485760 bytes in 0.601 s
[3/10] 10485760 bytes in 0.670 s
[4/10] 10485760 bytes in 0.663 s
[5/10] 10485760 bytes in 0.607 s
[6/10] 10485760 bytes in 0.844 s
[7/10] 10485760 bytes in 1.050 s
[8/10] 10485760 bytes in 0.661 s
[9/10] 10485760 bytes in 0.688 s
[10/10] 10485760 bytes in 0.665 s
Requests:         10
Total downloaded: 104.86 MB (104857600 bytes)
Average time:     0.716 s
Speed:            117.15 Mbit/s (14.64 MB/s)
```

## Installation

You need [uv](https://docs.astral.sh/uv/). It downloads Python 3.15 if you don't have it. The tool itself
uses only the standard library.

Install the command:

```bash
uv tool install git+https://github.com/kataytsev-works/download-speed
```

Run it once without installing:

```bash
uvx --from git+https://github.com/kataytsev-works/download-speed download-speed <url>
```

Or work from a clone, prefixing commands with `uv run`:

```bash
git clone https://github.com/kataytsev-works/download-speed.git
cd download-speed
uv run download-speed <url>
```

## Usage

```
usage: download-speed [-h] [-n COUNT] [-t TIMEOUT] [--version] url

Download a URL several times in a row and report the average request time, the total amount
downloaded and the download speed.

positional arguments:
  url                   http(s) URL to download

options:
  -h, --help            show this help message and exit
  -n, --count COUNT     number of sequential requests (default: 10)
  -t, --timeout TIMEOUT
                        socket timeout per operation, seconds (default: 30)
  --version             show program's version number and exit

Units: speed in Mbit/s and MB/s, volume in MB, with decimal prefixes (1 MB = 10^6 bytes, 1 Mbit =
10^6 bits).
```

Three requests with a 10 second timeout:

```
$ download-speed -n 3 -t 10 https://proof.ovh.net/files/1Mb.dat
[1/3] 1048576 bytes in 0.394 s
[2/3] 1048576 bytes in 0.400 s
[3/3] 1048576 bytes in 0.418 s
Requests:         3
Total downloaded: 3.15 MB (3145728 bytes)
Average time:     0.404 s
Speed:            20.76 Mbit/s (2.59 MB/s)
```

Progress goes to stdout line by line and errors go to stderr, so the report can be redirected to a file:

```bash
download-speed https://proof.ovh.net/files/10Mb.dat > report.txt
```

## Units

Speed is in megabits per second (Mbit/s), the unit ISPs and speed tests use, with megabytes per second next
to it. Sizes are in megabytes. Prefixes are decimal: 1 MB is 10^6 bytes, 1 Mbit is 10^6 bits, and
1 MB/s equals 8 Mbit/s.

## How it measures

Each request is timed from the moment it is sent until the last byte of the body has been read. That
includes the DNS lookup, TCP and TLS setup, and the wait for the server. Requests run one after another,
and each one opens its own connection.

The size is the number of body bytes actually received. Headers are not counted, compression is turned off
with `Accept-Encoding: identity`, and `Content-Length` is used only to detect a truncated body.

Speed is the total size divided by the total time. Averaging the speeds of individual requests would give
the fast requests too much weight.

The tool sends `Cache-Control: no-cache`, but a CDN may still answer from its cache.

With small files, connection setup takes most of the time and the result comes out well below the link's
bandwidth. Use a file of a few megabytes or more if bandwidth is what you want to know.

## Timeouts

`--timeout` applies to each socket operation (connecting, waiting for the response, reading a chunk), not
to the request as a whole. A slow download keeps going as long as data keeps arriving. A connection that
stays silent for longer than the timeout fails.

## Errors

If any request fails, the run stops without printing statistics, since they would only cover part of the
requests. The reason is printed to stderr:

```
$ download-speed https://proof.ovh.net/files/nope.dat
error: https://proof.ovh.net/files/nope.dat: HTTP 404 Not Found
```

The exit status is 0 on success and 1 when a request fails: an HTTP 4xx or 5xx status, a timeout, a DNS
failure, a refused or dropped connection, or a truncated body. Bad arguments exit with 2, Ctrl+C with 130.

Redirects are followed, and their time counts. Proxies from `HTTP_PROXY` and `HTTPS_PROXY` are used.

## Development

```bash
uv sync
uv run ruff check
uv run ruff format --check
uv run mypy
```

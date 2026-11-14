from importlib.metadata import PackageNotFoundError, version

DIST_NAME = "download-speed"

try:
    __version__ = version(DIST_NAME)
except PackageNotFoundError:
    __version__ = "0.0.0"


def main() -> None:
    print("Hello from download-speed!")

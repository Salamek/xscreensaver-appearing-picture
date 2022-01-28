
def main() -> None:
    """Entrypoint to the ``celery`` umbrella command."""
    from xscreensaver_appearing_picture.bin.xscreensaver_appearing_picture import main as _main
    _main()


if __name__ == '__main__':  # pragma: no cover
    main()

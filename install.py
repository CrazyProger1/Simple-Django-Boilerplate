import argparse


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        prog="",
        description="",
    )
    parser.add_argument()

    return parser.parse_args()


def install(arguments: argparse.Namespace) -> None:
    pass


if __name__ == '__main__':
    args = parse_args()
    install(args)

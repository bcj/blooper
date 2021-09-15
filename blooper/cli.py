"""
Run blooper from the command line
"""
from argparse import ArgumentParser
from typing import List, Optional


def main(input_args: Optional[List[str]] = None):
    """
    Run swim from the command line.
    """
    parser = ArgumentParser(description="Make bloops")
    args = parser.parse_args()

    raise NotImplementedError(args)


if __name__ == "__main__":
    main()

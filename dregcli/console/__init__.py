import argparse
import datetime
import json

from .handler import CommandHandler
from .reps import RepositoriesCommandHandler
from .tags import TagsCommandHandler
from .image import ImageCommandHandler
from .garbage import GarbageCommandHandler


def main():
    parser = argparse.ArgumentParser(
        prog="dregcli",
        description="Docker registry API v2 client",
    )
    parser.add_argument(
        '-u', '--user',
        help='user credentials login:password'
    )
    subparsers = parser.add_subparsers(help='sub-commands')

    RepositoriesCommandHandler.set_parser(subparsers)
    TagsCommandHandler.set_parser(subparsers)
    ImageCommandHandler.set_parser(subparsers)
    GarbageCommandHandler.set_parser(subparsers)

    arguments = parser.parse_args()
    if hasattr(arguments, 'func'):
        arguments.func(arguments)
    else:
        parser.print_help()

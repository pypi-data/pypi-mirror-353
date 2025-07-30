# import os
from argparse import ArgumentParser

from bobleesj.utils.cli import conda_forge, news, test

# from pathlib import Path


# FIXME: Implmement hidden config file for scalability
BOB_CONFIG_FILE = "~/.bobrc"
# config_file = os.environ.get("BOB_CONFIG_FILE", BOB_CONFIG_FILE)
# config_file = Path(os.path.expandvars(config_file)).expanduser()
# exist_config = config_file.exists()
config = {
    "feedstock_path": "/Users/macbook/downloads/dev/feedstocks",
}

# FIXME: implement `bob test package`


def test_package(args):
    test.build_pytest()


def test_release(args):
    test.build_check_release()


def update_feedstock(args):
    conda_forge.main(config)


def add_news(args):
    news.add_news_item(args)


def add_nonews(args):
    news.add_no_news_item(args)
    print(f"Adding NO news with message: {args.message}")


def main():
    parser = ArgumentParser(
        description="Save time managing software packages."
    )
    subparsers = parser.add_subparsers(dest="command", required=True)
    # --- Test command ---
    parser_update = subparsers.add_parser(
        "test", help="Test the package with a new conda environment."
    )
    update_subparsers = parser_update.add_subparsers(
        dest="subcommand", required=True
    )
    parser_test_package = update_subparsers.add_parser(
        "package",
        help="Test the single package.",
    )
    parser_test_package.set_defaults(func=test_package)

    parser_test_release = update_subparsers.add_parser(
        "release",
        help="Test the release condition for the package.",
    )
    parser_test_release.set_defaults(func=test_release)

    # --- Update Command ---
    parser_update = subparsers.add_parser(
        "update", help="Update repositories and packages."
    )
    update_subparsers = parser_update.add_subparsers(
        dest="subcommand", required=True
    )
    parser_feedstock = update_subparsers.add_parser(
        "feedstock",
        help="Prepare to create a PR to the conda-forge/main with updated "
        "version and SHA256 in meta.yaml.",
    )
    parser_feedstock.set_defaults(func=update_feedstock)

    # --- Add command ---
    parser_add = subparsers.add_parser("add", help="Add news entries.")
    add_subparsers = parser_add.add_subparsers(
        dest="subcommand", required=True
    )

    def add_news_flags(p):
        p.add_argument("-m", "--message", required=True, help="News item.")
        p.add_argument("-a", action="store_true", help="Added")
        p.add_argument("-c", action="store_true", help="Changed")
        p.add_argument("-d", action="store_true", help="Deprecated")
        p.add_argument("-r", action="store_true", help="Removed")
        p.add_argument("-f", action="store_true", help="Fixed")
        p.add_argument("-s", action="store_true", help="Security")

    parser_add_news = add_subparsers.add_parser(
        "news", help="Add a news entry."
    )
    add_news_flags(parser_add_news)
    parser_add_news.set_defaults(func=add_news)
    parser_add_nonews = add_subparsers.add_parser(
        "no-news", help="Add a no-news entry."
    )
    add_news_flags(parser_add_nonews)
    parser_add_nonews.set_defaults(func=add_nonews)
    # Parse and run
    args = parser.parse_args()
    args.func(args)


if __name__ == "__main__":
    """
    Examples:
    ---------
    >>> bob test package
    >>> bob update feedsetock
    >>> bob add news -a -m "Add awesome news!"
    >>> bob add no-news -m "A grammatical fix"
    """
    main()

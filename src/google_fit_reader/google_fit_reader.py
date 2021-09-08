import argparse


def main():
    args = parse_args(sys.argv[1:])


def parse_args(args):
    """

    :param list args: The list of arguments to parse.
    :return argparse.Namespace: An object which contains all parsed arguments as attributes.

    Convert argument strings to objects and assign them as attributes of the namespace.
    Return the populated namespace.
    """
    parser = argparse.ArgumentParser(
        description="A command line utility to help create a rich multimedia library out of your backup movie collection."
    )
    parser.add_argument(
        "--directory", "-d", type=str, help="The directory containing activity files."
    )
    parser.add_argument(
        "--file_type",
        "-f",
        type=str,
        default="json",
        help="Specify the type of file to parse.",
    )
    parser.add_argument(
        "--output_filename",
        "-o",
        type=str,
        default="google_fit.csv",
        help="Specify the name of the output file.",
    )
    return parser.parse_args(args)


class GoogleFitReader:
    def __init__(self, directory, file_type, output_filename):
        self._directory = directory
        self._file_type = (file_type,)
        self._output_filename = output_filename

    def _parse(self):
        pass

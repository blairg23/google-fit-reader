import argparse
import sys
import os
import glob
import xml.etree.ElementTree as ET
import re


def main():
    args = parse_args(sys.argv[1:])

    google_fit_reader = GoogleFitReader(
        directory=args.directory,
        file_type=args.file_type,
        output_filename=args.output_filename,
    )
    google_fit_reader.parse()


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
        self._file_type = file_type
        self._file_regex = "*." + file_type
        self._output_filename = output_filename

    def parse(self):
        if self._file_type.lower() == 'json':
            self._parse_json()
        elif self._file_type.lower() == 'tcx':
            self._parse_xml()

    def _parse_json(self):
        pass
    
    def _parse_xml(self):
        # for filename in os.listdir(self._directory):
        #     print('filename: ', filename)

        glob_path = os.path.join(self._directory, self._file_regex)
        print(glob_path)
        for filepath in glob.iglob(glob_path): 
            print("filepath: ", filepath)
            tree = ET.parse(filepath)
            # print('tree: ', tree)
            root = tree.getroot()
            # print('root: ', root)
            # print('dir(root): ', dir(root))
            # print('root.attrib: ', root.attrib)
            # print('root.items: ', root.items())
            # print('root.keys: ', root.keys())
            # print('root.tag: ', root.tag)
            # print('root.namespace: ', self._get_namespace(element=root))
            namespace = self._get_namespace(element=root)

            # print(ET.dump(root))
            for activities in root.iter(namespace + 'Activities'):
                for activity in activities.iter(namespace + 'Activity'):
                    timestamp = activity.find(namespace + 'Id')
                    lap = activity.find(namespace + 'Lap')
                    distance_meters = float(lap.find(namespace + 'DistanceMeters').text)
                    distance_miles = distance_meters / 1609.0
                    total_time_seconds = float(lap.find(namespace + 'TotalTimeSeconds').text)
                    total_time_minutes = total_time_seconds / 60.0
                    print('timestamp: ', timestamp)
                    print('distance in miles: ', distance_miles)
                    print('total time in minutes: ', total_time_minutes)
                    print('-----')
        

    def _get_namespace(self, element):
        m = re.match(r'\{.*\}', element.tag)
        return m.group(0) if m else ''
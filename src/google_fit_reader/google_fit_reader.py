import argparse
import glob
import json
import os
import re
import sys
import pytz
import datetime
from dateutil import parser
from dateutil.tz import gettz
import xml.etree.ElementTree as ET


def main():
    args = parse_args(sys.argv[1:])

    google_fit_reader = GoogleFitReader(
        directory=args.directory,
        file_type=args.file_type,
        output_filename=args.output_filename,
        timezone=args.timezone,
        verbose=args.verbose,
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
        choices=["tcx", "json"],
        help="Specify the type of file to parse.",
    )
    parser.add_argument(
        "--output_filename",
        "-o",
        type=str,
        default="google_fit.csv",
        help="Specify the name of the output file.",
    )
    parser.add_argument(
        "--timezone",
        "-t",
        type=str,
        default="Americas/Denver",
        help="Specify the timezone.",
    )
    parser.add_argument(
        "--verbose",
        "-v",
        type=bool,
        default=False,
        choices=[True, False],
        help="Specify verbosity of the output."
    )
    return parser.parse_args(args)


class GoogleFitReader:
    def __init__(self, directory, file_type, output_filename, timezone, verbose=False):
        self._directory = directory
        self._file_type = file_type
        self._file_regex = "*." + file_type
        self._glob_path = os.path.join(self._directory, self._file_regex)
        self._output_filename = output_filename
        self._timezone=timezone
        self._verbose = verbose

    def parse(self):
        if self._file_type.lower() == "json":
            self._parse_json()
        elif self._file_type.lower() == "tcx":
            self._parse_xml()

    def _parse_json(self):
        """
        Parses a JSON document containing Google Fit data and returns as CSV data.
        """
        headers = ["timestamp (utc)", f"timestamp ({self._timezone})", "activity", "distance (miles)", "duration (min)"]
        data = {}

        for filepath in glob.iglob(self._glob_path): 
            with open(filepath) as infile:
                activity = json.load(infile)
            activity_name = activity.get("fitnessActivity")
            timestamp = activity.get("startTime")
            print('timestamp: ', timestamp)
            local_timestamp = self._translate_timestamp(timestamp, to_timezone=self._timezone)
            total_time_seconds = float(activity.get("duration").replace("s", ""))
            total_time_minutes = str(total_time_seconds / 60.0)
            aggregate = activity.get("aggregate")
            for element in aggregate:
                if element.get("metricName") == "com.google.distance.delta":
                    distance_meters = element.get("floatValue")
                    distance_miles = str(distance_meters / 1609.0)
            
            if self._verbose:
                print("filepath: ", filepath)
                print("timestamp: ", timestamp)
                print("local timestamp: ", local_timestamp)
                print("activity: ", activity_name)
                print("distance in miles: ", distance_miles)
                print("total time in minutes: ", total_time_minutes)
                print("-----")

            if timestamp in data:
                raise Exception(f"ERROR: Duplicate timestamps: {timestamp}")
            else:
                data[timestamp] = {
                    "local_timestamp": local_timestamp,
                    "activity": activity_name,
                    "distance": distance_miles,
                    "duration": total_time_minutes,
                }
        self._write_csv(headers=headers, data=data)
    
    def _parse_xml(self):
        """
        Parses an XML document containing Google Fit data and returns as CSV data.
        """
        # for filename in os.listdir(self._directory):
        #     print("filename: ", filename)
        def get_namespace(element):
            m = re.match(r"\{.*\}", element.tag)
            return m.group(0) if m else ""

        for filepath in glob.iglob(self._glob_path):
            tree = ET.parse(filepath)
            # print("tree: ", tree)
            root = tree.getroot()
            # print("root: ", root)
            # print("dir(root): ", dir(root))
            # print("root.attrib: ", root.attrib)
            # print("root.items: ", root.items())
            # print("root.keys: ", root.keys())
            # print("root.tag: ", root.tag)
            # print("root.namespace: ", self._get_namespace(element=root))
            namespace = get_namespace(element=root)

            # print(ET.dump(root))
            for activities in root.iter(namespace + "Activities"):
                for activity in activities.iter(namespace + "Activity"):
                    activity_name = activity.attrib.get("Sport")
                    timestamp = activity.find(namespace + "Id").text
                    lap = activity.find(namespace + "Lap")
                    distance_meters = float(lap.find(namespace + "DistanceMeters").text)
                    distance_miles = str(distance_meters / 1609.0)
                    total_time_seconds = float(lap.find(namespace + "TotalTimeSeconds").text)
                    total_time_minutes = str(total_time_seconds / 60.0)
                    if self._verbose:
                        print("filepath: ", filepath)
                        print("timestamp: ", timestamp)
                        print("activity: ", activity_name)
                        print("distance in miles: ", distance_miles)
                        print("total time in minutes: ", total_time_minutes)
                        print("-----")
                    sys.exit()

    def _translate_timestamp(self, timestamp, from_timezone=pytz.utc, to_timezone="America/Denver"):
        """
        :param str timestamp: A string containing the timestamp to translate.
        :param str from_timezone: A string containing the timezone to translate from.
        :param str to_timezone: A string containing the timezone to translate to.
        """
        old_datetime = parser.parse(timestamp)
        new_datetime = old_datetime.astimezone(gettz(to_timezone)).strftime("%Y-%m-%dT%H:%M:%S:%f")
        if self._verbose:
            print("old datetime: ", old_datetime)
            print("new datetime: ", new_datetime)
        return new_datetime        

    def _write_csv(self, headers, data):
        """
        :param list headers: A list containing the headers for the CSV
        :param dict data: A dict containing row data to write to CSV

        Writes a CSV, given the headers and row data
        """
        output_filepath = os.path.join("data", self._output_filename)
        with open(output_filepath, "a+") as outfile:
            headers = ",".join(headers)
            outfile.write(headers + "\n")
            for key,values in data.items():
                output_line = key + "," + ",".join(values.values())
                outfile.write(output_line + "\n")

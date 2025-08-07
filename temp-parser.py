#!/bin/env python3
"""
Small program that parses temperature data from an input file,
then saves the data in a clean csv file and presents a graph of it.
"""
import argparse
import re
import csv
import pandas as pd
import matplotlib.pyplot as plt
import time
import os


def _next_table_name(num: int) -> str:
    p_num = str(num).zfill(3)
    return "Output/temp_csv_" + p_num + ".csv"


def _next_png_name(num: int) -> str:
    p_num = str(num).zfill(3)
    return "Output/temperature_data_" + p_num + ".png"


def _switch_out_file(tables, num: int):
    tables.append(open(_next_table_name(num), 'w+', newline=''))
    out_writer = csv.writer(tables[num])
    out_writer.writerow(['datetime', 'device', 'temperature'])
    return out_writer


def main():
    # parser which accepts 3 arguments
    parser = argparse.ArgumentParser()
    parser.add_argument("--inputfile", help="The path to the input file",
                        default=None)
    parser.add_argument("-g", "--graph", help="display a graph of the data",
                        default=False, action="store_true")
    parser.add_argument("-s", "--save_output",
                        help="saves the output graphs as PNGs",
                        default=False, action="store_true")
    parser.add_argument("-r", "--report",
                        help="create an index.html page with the graph(s)",
                        default=False, action="store_true")
    parser.add_argument("-c", "--cutoff", default=20,
                        help="max time in minutes between two table entries")
    # TODO: ADD A --HELP ARGUMENT
    args = parser.parse_args()

    # Try to safely open the files passed to us
    try:
        in_file = open(args.inputfile, "r")
    except OSError:
        print("Unable to open input file " + args.filename)
        exit(1)

    try:
        os.makedirs("Output", exist_ok=True)
    except OSError:
        print("Error creating output directory")
        exit(1)
    """
    TODO: update this documentation to explain the multi-charting process

    Look through each line of the input file. Each line should be in the form:
    MON DD HH:MM:SS .(*?) [({"A":"DEVICENAME", "T":(TEMP|null)})*?]
    The number of (A,T) pairs may differ from line to line.
    The values of T may be null due to issues in temperature reporting.

    A line with n (A,T) pairs will be written into output file as n lines,
    with each (A,T) pair having its own line. This is for ease of graphing.
    """

    out_tables = []
    out_writer = _switch_out_file(out_tables, len(out_tables))
    prev_date = None
    for line in in_file:
        # Skip lines that we suspect don't fit our pattern
        if line.find("heatmon") == -1 or line.find("ERROR") != -1:
            continue
        mon = time.strptime(line[:3], '%b').tm_mon
        t = pd.to_datetime(line[4:15], format='%d %H:%M:%S')
        t = t.replace(month=mon, year=time.localtime().tm_year)
        if prev_date and (t - prev_date).seconds > (args.cutoff * 60):
            # Switch to new table
            out_writer = _switch_out_file(out_tables, len(out_tables))
        prev_date = t
        device_matches = re.finditer(r'A":"(.*?)"', line)
        temp_matches = re.finditer(r'T":(.*?|null)}', line)
        devices = []
        temps = []
        for device_match in device_matches:
            devices.append(device_match.group(1))
        for temp_match in temp_matches:
            temps.append(temp_match.group(1))
        for i in range(len(temps)):
            out_writer.writerow([t, devices[i], temps[i]])

    for file in out_tables:
        file.flush()
        file.close()

    for file_num in range(len(out_tables)):
        file = out_tables[file_num]
        df = pd.read_csv(file.name, parse_dates=['datetime'])
        fig, ax = plt.subplots()
        for device, sub_df in df.groupby('device'):
            sub_df.plot(ax=ax, x='datetime', y='temperature', label=device)
        ax.legend(title='devices')
        plt.legend(bbox_to_anchor=(1, 1))
        plt.tight_layout()
        if args.save_output or args.report:
            plt.savefig(_next_png_name(file_num))
        if args.graph:
            plt.show()

    if args.report:
        # write an index.html page with the graphs we made
        with open('temperature-report.html', 'w') as f:
            f.write("<!DOCTYPE HTML> \n <html> \n <b>")
            for file_num in range(len(out_tables)):
                f.write('<img src=\"' +
                        _next_png_name(file_num) +
                        '\" alt=\"graph 1\">')
            f.write("</b> \n </html>")


main()

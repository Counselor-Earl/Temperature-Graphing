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
import matplotlib.dates as mdates
import time
import os

_output_dir_name = "Temp_Graphing_"
_max_legend_entries = 4

def _next_table_name(num: int, timestamp:str) -> str:
    p_num = str(num).zfill(3)
    return _output_dir_name + timestamp + "/temp_csv_" + p_num + ".csv"


def _next_png_name(num: int, timestamp:str) -> str:
    p_num = str(num).zfill(3)
    return _output_dir_name + timestamp + "/temperature_data_" + p_num + ".png"


def _switch_out_file(tables, num: int, timestamp):
    tables.append(open(_next_table_name(num, timestamp), 'w+', newline=''))
    out_writer = csv.writer(tables[num])
    out_writer.writerow(['datetime', 'device', 'temperature'])
    return out_writer


def main():
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
        print("Unable to open input file " + args.inputfile)
        exit(1)

    _timestamp_str = time.ctime()[4:13].replace(' ', '_')
    try:
        os.makedirs((_output_dir_name + _timestamp_str), exist_ok=True)
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
    rig = None
    _start = None
    _end = None
    out_tables = []
    out_writer = _switch_out_file(out_tables, len(out_tables), _timestamp_str)
    prev_date = None
    for line in in_file:
        # Skip lines that we suspect don't fit our pattern
        if line.find("heatmon") == -1 or line.find("ERROR") != -1:
            continue
        mon = time.strptime(line[:3], '%b').tm_mon
        t = pd.to_datetime(line[4:15], format='%d %H:%M:%S')
        t = t.replace(month=mon, year=time.localtime().tm_year)
        if prev_date and (t - prev_date).seconds > (int(args.cutoff) * 60):
            # Switch to new table
            out_writer = _switch_out_file(out_tables, len(out_tables), _timestamp_str)
        prev_date = t
        if rig is None:
            rig = re.search(r':.. .*? ', line)
            rig = rig.group(0)[4:-1] if rig else None
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

    in_file.close()

    date_format = mdates.DateFormatter('%H:%M')

    for file_num in range(len(out_tables)):
        file = out_tables[file_num]
        df = pd.read_csv(file.name)
        df['datetime'] = pd.to_datetime(df['datetime'], format="%Y-%m-%d %H:%M:%S")
        _, ax = plt.subplots()
        for device, sub_df in df.groupby('device'):
            sub_df.plot(ax=ax, x='datetime', y='temperature', label=device, x_compat=True)
        _, labels = plt.gca().get_legend_handles_labels()
        ax.legend(title='devices')
        plt.legend(bbox_to_anchor=(1, 1))
        ax.xaxis.set_major_formatter(date_format)
        _start = str(df['datetime'].iloc[0].month) + "/" + str(df["datetime"].iloc[0].day)
        _end = str(df['datetime'].iloc[-1].month) + "/" + str(df["datetime"].iloc[-1].day)
        plt.title(f"{rig} From {_start} to {_end}")
        plt.xlabel("Time")
        plt.ylabel("Temperature (" + chr(176) + "C)")
        _, labels = plt.gca().get_legend_handles_labels()
        if len(labels) > _max_legend_entries:
            plt.gca().get_legend().remove()
        if args.save_output or args.report:
            plt.savefig(_next_png_name(file_num, _timestamp_str))
        if args.graph:
            plt.show()

    if args.report:
        # write an index.html page with the graphs we made
        with open('temperature_report_' + _timestamp_str + '.html', 'w') as f:
            f.write("<!DOCTYPE HTML> \n <html> \n <b>")
            for file_num in range(len(out_tables)):
                f.write('<img src=\"' +
                        _next_png_name(file_num, _timestamp_str) +
                        '\" alt=\"graph 1\">')
            f.write("</b> \n </html>")


main()

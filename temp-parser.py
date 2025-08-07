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


def main():
    # parser which accepts 3 arguments
    parser = argparse.ArgumentParser()
    parser.add_argument("--inputfile", help="The path to the input file",
                        default=None)
    parser.add_argument("--outputfile", help="The name of the output file",
                        default="temp-csv-000.csv")
    parser.add_argument("-g", "--graph", help="display a graph of the data",
                        default=False, action="store_true")
    parser.add_argument("-s", "--save_output", help="saves the output graphs as PNGs",
                        default=False, action="store_true")
    parser.add_argument("-r", "--report", help="create an index.html page with the graph(s)",
                        default=False, action="store_true")
    args = parser.parse_args()

    # Try to safely open the files passed to us
    try:
        in_file = open(args.inputfile, "r")
    except OSError:
        print("Unable to open input file " + args.filename)
        exit(1)
    try:
        out_file = open(args.outputfile, "w", newline='')
    except OSError:
        print("Unable to create open/create new output file " + args.output)
        exit(1)

    # Files are safely open. Create a csvwriter to neatly write our output
    out_writer = csv.writer(out_file)
    out_writer.writerow(['datetime', 'device', 'temperature'])

    """
    Look through each line of the input file. Each line should be in the form:
    MON DD HH:MM:SS .(*?) [({"A":"DEVICENAME", "T":(TEMP|null)})*?]
    The number of (A,T) pairs may differ from line to line.
    The values of T may be null due to issues in temperature reporting.

    A line with n (A,T) pairs will be written into output file as n lines,
    with each (A,T) pair having its own line. This is for ease of graphing.
    """
    for line in in_file:
        # filter out any line that we suspect does not match this format
        # TODO: Separate dates with gaps of >20~ minutes into different plots
        if line.find("heatmon") == -1 or line.find("ERROR") != -1:
            continue
        mon = time.strptime(line[:3], '%b').tm_mon
        t = pd.to_datetime(line[4:15], format='%d %H:%M:%S')
        t = t.replace(month=mon, year=time.localtime().tm_year)
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

    # We are done with our input file and can safely close it
    in_file.close()
    out_file.close()

    # If we are not graphing our data, safely terminate
    if not args.graph and not (args.save_output or args.report):
        exit(0)

    # graph of data using panda's dataframe and matplotlib for visualization
    df = pd.read_csv(args.outputfile, parse_dates=['datetime'])
    fig, ax = plt.subplots()
    for device, sub_df in df.groupby('device'):
        sub_df.plot(ax=ax, x='datetime', y='temperature', label=device)
    ax.legend(title='devices')
    plt.legend(bbox_to_anchor=(1, 1))
    plt.tight_layout()
    if args.save_output:
        plt.savefig("temp-graph-001.png") # TODO: dynamic naming
    if args.graph:
        plt.show(block=True)

    if args.report:
        # write an index.html page with the graphs we made
        with open('index.html', 'w') as f:
            f.write("<!DOCTYPE HTML> \n <html> \n <b>")
            f.write('<img src=\"temp-graph-001.png\" alt=\"graph 1\">')
            f.write("</b> \n </html>")

main()

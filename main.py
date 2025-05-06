"""
Small program that parses temperature data from an input file,
then saves the data in a clean csv file and presents a graph of it.
"""
import argparse
import re
import csv
import pandas as pd
import matplotlib.pyplot as plt


def main():
    # standard parser which accepts 3 arguments
    parser = argparse.ArgumentParser()
    parser.add_argument("inputfile", help="The path to the input file")
    parser.add_argument("outputname", help="The name of the output file")
    parser.add_argument("-g", "--graph", help="display a graph of the data", action="store_true")
    args = parser.parse_args()

    # Try to safely open the files passed to us
    try:
        in_file = open(args.inputfile, "r")
    except OSError:
        print("Unable to open input file " + args.filename)
        exit(1)
    try:
        out_file = open(args.outputname, "w", newline='')
    except OSError:
        print("Unable to create open/create new output file " + args.output)
        exit(1)

    # Files are safely open. Create a csvwriter to neatly write our output
    out_writer = csv.writer(out_file)
    out_writer.writerow(['datetime', 'device', 'temperature'])

    """
    Look through each line of the input file. Each line should be in the form:
    MON 00 00:00:00 .(*?) [({"A":"DEVICENAME", "T":(TEMP|null)})*?]
    The number of (A,T) pairs may differ from line to line.
    The values of T may be null due to issues in temperature reporting.
    
    A line with n (A,T) pairs will be written into the CSV output file as n lines,
    with each (A,T) pair having its own line. This is for ease of graphing.
    """
    for line in in_file:
        t = pd.to_datetime(line[7:15])
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

    # If we are not graphing our data, the program is complete and may safely terminate
    if not args.graph:
        exit(0)

    # simple graph of the data using panda's dataframe and matplotlib for visualization
    df = pd.read_csv(args.outputname, parse_dates=['datetime'])
    fig, ax = plt.subplots()
    for device, sub_df in df.groupby('device'):
        sub_df.plot(ax=ax, x='datetime', y='temperature', label=device)
    ax.legend(title='devices')
    plt.show(block=True)


main()

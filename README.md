This is a small program which parses temperature data from a log file, writes it to a csv file, and optionally graphs it.

![Example graph](https://github.com/Counselor-Earl/Temperature-Graphing/blob/main/Temp_data_0.png)

The log file must be constructed out of lines that all follow this format:
~~~
MON DD HH:MM:SS .(*?) [({"A":"DEVICENAME", "T":(TEMP|null)})*?]
~~~
Example line:
~~~
Mar 27 15:38:00 ct521b-18cb heatmon[69756]: [{"A":"mt7915_phy2-pci-0f00","T":72.000}]
~~~

**Usage**
This program expects two positional arguments: inputfile and outputfile. Inputfile is the path to the log file. Outputfile is the name of the output csv file.

Run the program with **-g** or **--graph** to perform graphing. The program will not graph by default.

**Example Usage:**
~~~
python main.py input.txt output.csv -g
~~~

The number of (A, T) device-temp pairs may change from line to line. The log file need not be sorted.

The temperature value _may_ be null, as issues may appear in automated temperature logging. Null values are not graphed (note the presence of an extra, ungraphed device in the key above).

Behavior is undefined for null device names.

_Liam Reynolds, 2025_

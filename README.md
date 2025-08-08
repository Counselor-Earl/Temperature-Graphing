This is a small program which parses temperature data from a log file and creates a visual report.
The program will split the input data into separate charts if there is more than *cutoff* minutes between two data points.

![Example graph](https://github.com/Counselor-Earl/Temperature-Graphing/blob/main/Temp_data_0.png)

The log file must be constructed out of lines that all follow this format:
~~~
MON DD HH:MM:SS RIGNAME [({"A":"DEVICENAME", "T":(TEMP|null)})*?]
~~~
Example line:
~~~
Mar 27 15:38:00 ct521b-18cb heatmon[69756]: [{"A":"mt7915_phy2-pci-0f00","T":72.000}]
~~~

**Usage**
This program requires one argument: **--inputfile**. Inputfile is the path to the log file.

The **-g** or **--graph** argument will cause it to render a live graph with the matplotlib library.

The **-s** or **--save_output** argument will save the graphs as PNGs to an output directory.

The **-r** or **--report** argument will generate an html report page containing all the created graphs (this will also save the graph PNGs).

The **-c** or **--cutoff** argument lets the user manually set the cutoff time at which charts should be separated (default: 20 minutes).

**Example Usage:**
~~~
python temp-parser.py input.txt -g

python temp-parser.py input.txt -r -c 10
~~~

The number of (A, T) device-temp pairs may change from line to line. The log file need not be sorted.

The temperature value _may_ be null, as issues may appear in automated temperature logging. Null values are not graphed (note the presence of an extra, ungraphed device in the key above).

Behavior is undefined for null device names.

_Liam Reynolds, 2025_

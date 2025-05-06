This is a small program which parses temperature data from a log file, writes it to a csv file, and optionally graphs it.

The log file must be constructed out of lines that all follow this format:
~~~
MON DD HH:MM:SS .(*?) [({"A":"DEVICENAME", "T":(TEMP|null)})*?]
~~~
Example line:
~~~
Mar 27 15:38:00 ct521b-18cb heatmon[69756]: [{"A":"mt7915_phy2-pci-0f00","T":72.000}]
~~~

![Example graph](https://github.com/Counselor-Earl/Temperature-Graphing/blob/main/Temp_data_0.png)


The number of (A, T) device-temp pairs may change from line to line. The log file need not be sorted.

The temperature value _may_ be null, as issues may appear in automated temperature logging. Null values are not graphed.

Behavior is undefined for null device names.

_Liam Reynolds, 2025_

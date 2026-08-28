---
key: pypi/dts
source: pypi
name: dts
package: dts
description: Generate sequence of datatimes, like seq
registry_url: https://pypi.org/project/dts/
version: 0.1.3
last_release: '2018-05-13'
repository_url: https://github.com/KwangYeol/dts
repository_declared_in_metadata: true
license_stated: null
author: Kwangyeol Ryu
probes:
- pypi:simple-index-sweep
probe_class: broad-acronym
found_by:
- search
first_seen: '2026-08-28'
---

dts: Generate sequence of datetimes, like seq
=============================================

## Sequece of dates

`dts` generate sequence of datetimes. 

```
$ dts 20180401 20180403
20180401
20180402
20180403
```

If you do it using `seq`, it will like below.

```bash
$ seq 1 3
1
2
3
$ seq -f '%02g' 1 3 | xargs -I {} echo "201804{}"
20180401
20180402
20180403
```

## Install

```bash
pip install dts
```


## How to use: Simple

```bash
$ dts -h
usage: dts [-h] [-i INTERVAL] [-f FORMAT] FIRST LAST

dts is a seq util for datetimes

Examples:

  $ dts 20180501 20180503
  20180501
  20180502
  20180503

  $ dts 20180501-0900 20180501-1200 -i h1 -f '%Y-%m-%dT%H:%M:%S'
  2018-05-01T09:00:00
  2018-05-01T10:00:00
  2018-05-01T11:00:00
  2018-05-01T12:00:00

Github: https://github.com/KwangYeol/dts

positional arguments:
  FIRST                 first date of the seq. For example, 2018-05-01, 20180501, 20180501-0900, 2018-05-01T09:00
  LAST                  last date of the seq. See also, FIRST

optional arguments:
  -h, --help            show this help message and exit
  -i INTERVAL, --interval INTERVAL
                        interval: h1, d1, w1. default value is d1
  -f FORMAT, --format FORMAT
                        see also, datetime.strftime
```

* `-i`: It has two parts. (time unit) + (interval). 
  - time unit: `h` menas hours, `d` means days, and `w` menas weeks 
  - interval: numbers
  - `h1` means 1-hour interval, `d3` means 3-day interval, etc.
  - default value is `d1`

* `-f`: It has datetime format. See this (https://docs.python.org/2/library/datetime.html#strftime-strptime-behavior)


## How to use: with Pipeline

```bash
$ dts 20180401 20180430 -i d7
20180401
20180408
20180415
20180422
20180429

$ dts 20180510-0900 20180510-1400 -i h1 -f '%Y%m%d-%H00'
20180510-0900
20180510-1000
20180510-1100
20180510-1200
20180510-1300
20180510-1400

$ dts 20180510-0900 20180510-1400 -i h1 -f '%Y-%m-%dT%H:00'
2018-05-10T09:00
2018-05-10T10:00
2018-05-10T11:00
2018-05-10T12:00
2018-05-10T13:00
2018-05-10T14:00
```


### How to use

For examle, you have hive table named `credit` which has daily partition `yyyymmdd` like below.

```bash
hadoop fs -ls /hive/warehouse/sales.db/credit/yyyymmdd=20180401
```

You can find the data size in some range with `dts`.

```bash
$ dts 20180401 20180410 | xargs -I {} hadoop fs -ls /hive/warehouse/sales.db/credit/yyyymmdd={}
```


## Development

python setup.py install
python setup.py sdist 
python setup.py sdist bdist bdist_wheel

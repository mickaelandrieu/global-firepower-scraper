 # Global Fire Power Scraper
 

## How to use it ?

``
pip install globalfirepower-scraper
``

```python
from globalfirepower import GlobalFirePowerScraper

gfi_scraper = GlobalFirePowerScraper()

print(gfi_scraper.get_armies_information())
```

Exemple of output:

```
     rank           name  power_index progress                        id Population  ... Fit-for-Service Reaching Mil Age Annually Tot Military Personnel (est.) Active Personnel Reserve Personnel Paramilitary Total
0       1  United States       0.0453       up  united-states-of-america          3  ...       122274415                   4354979                       1832000          1390000            442000                  0
1       2         Russia       0.0501       up                    russia          9  ...        46681219                   1280887                       1350000           850000            250000             250000
2       3          China       0.0511       up                     china          1  ...       619268690                  19570568                       3134000          2000000            510000             624000
3       4          India       0.0979       up                     india          2  ...       496891621                  22768619                       5132000          1450000           1155000            2527000
4       5          Japan       0.1195       up                     japan         11  ...        43391178                   1122186                        309000           240000             55000              14000
..    ...            ...          ...      ...                       ...        ...  ...             ...                       ...                           ...              ...               ...                ...
137   138        Liberia       8.5213   stable                   liberia        113  ...         1835339                     62568                          2000             2000                 0                  0
138   139        Somalia      11.8854     down                   somalia         72  ...         1669060                    120946                         17500            17500                 0                  0
139   140         Kosovo      13.9136       up                    kosovo        134  ...          727657                     17417                          6500             3500              3000                  0
140   141         Bhutan      35.8958     down                    bhutan        138  ...          118324                      4287                          8000             8000                 0                  0
141   142        Iceland      78.6623   stable                   iceland        142  ...           48070                      1779                             0                0                 0                  0

[142 rows x 60 columns]
```
## Deploy upgrade on PyPi

```
# Build
python setup.py sdist bdist_wheel

# Test
python -m pip install -e .
python

>>> from globalfirepower import GlobalFirePowerScraper
>>> gfi_scraper = GlobalFirePowerScraper()
>>> print(gfi_scraper.get_armies_information())
```

## LICENCE

This works is under MIT License.

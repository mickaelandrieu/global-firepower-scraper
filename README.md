 # Global Fire Power Scraper
 

## How to use it ?

``
pip install globalfirepower-scraper
``

```python
from globalfirepower import GlobalFirePowerScraper

gfi_scraper = GlobalFirePowerScraper

print(gfps.get_country_ranking_table())
```

Exemple of output:

```
     rank           name  power_index progress                        id
0       1  United States       0.0453       up  united-states-of-america
1       2         Russia       0.0501       up                    russia
2       3          China       0.0511       up                     china
3       4          India       0.0979       up                     india
4       5          Japan       0.1195       up                     japan
..    ...            ...          ...      ...                       ...
137   138        Liberia       8.5213   stable                   liberia
138   139        Somalia      11.8854     down                   somalia
139   140         Kosovo      13.9136       up                    kosovo
140   141         Bhutan      35.8958     down                    bhutan
141   142        Iceland      78.6623   stable                   iceland
```
## Deploy upgrade on PyPi

```
# Build
python setup.py sdist bdist_wheel

# Test
python -m pip install -e .
python

>>> from globalfirepower import GlobalFirePowerScraper
>>> gfi_scraper = GlobalFirePowerScraper
>>> print(gfps.get_country_ranking_table())
```

## LICENCE

This works is under MIT License.

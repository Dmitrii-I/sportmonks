# Changelog


## 0.1.2 (2018-08-26)
* Fix bug in `SoccerApiV2.season_results()` default value. Default value must an empty tuple not `None`.
* Stop caching `SoccerApiV2.season()` method. When `season()` was called and the cache was empty, a call to `seasons()` was made to populate the cache. This proved to be too slow to be useful.

## 0.1.1 (2018-06-30)
* Make `pip install sportmonks` work with Python version 3.5.2 or later instead of 3.5.3 or later. Python version 3.5.2 is popular because it is the default Python 3 on Ubuntu 16.

## 0.1.0 (2018-06-30)
* First version.


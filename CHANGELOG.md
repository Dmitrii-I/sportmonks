# Changelog


## 1.0.0 (2018-12-01)
* Stop caching methods. As such caching has been removed from `SoccerApiV2.bookmaker`, `SoccerApiV2.continent`, `SoccerApiV2.country`, `SoccerApiV2.league`. Caching can still be done by callers with the `functools.lru_cache` decorator.
* Fix bug in `SoccerApiV2.fixtures` and `SoccerApiV2.fixtures_today`. When parameter `league_ids` was specified and the resulting response contained more than 100 fixtures, then the fixtures beyond the first 100 contained also fixtures not belonging to the specified `league_ids`. 
* Parameter `include` has been renamed to `includes`. This name is better because it can contain zero or more includes, not zero or one.
* Accept any iterable in the `includes` parameter, not just tuples. Lists, sets, and other iterables with a `__getitem__` magic method will work. Strings, even though iterables, are converted to a one-element list. This allows also to pass single include lazily as `includes='continent'`, instead of `includes=['continent']`. In fact this could also be considered as a bug fix, because in previous versions the strings were accepted too, but were passed as single character includes and SportMonks API was not raising any error.
* Remove API token from logs for better security. Note, that the API token will still appear unedited in logs of `requests` and `urllib3` packages.

## 0.1.2 (2018-08-26)
* Fix bug in `SoccerApiV2.season_results()` default value. Default value must an empty tuple not `None`.
* Stop caching `SoccerApiV2.season()` method. When `season()` was called and the cache was empty, a call to `seasons()` was made to populate the cache. This proved to be too slow to be useful.

## 0.1.1 (2018-06-30)
* Make `pip install sportmonks` work with Python version 3.5.2 or later instead of 3.5.3 or later. Python version 3.5.2 is popular because it is the default Python 3 on Ubuntu 16.

## 0.1.0 (2018-06-30)
* First version.


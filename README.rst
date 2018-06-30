sportmonks
==========

This Python package implements the SportMonks HTTP API. SportMonks offers HTTP APIs for soccer and formula 1, with
additional sports on its roadmap. This package implements the soccer API, with plans to implement additional sports in
near future.

Example
=======

.. code-block:: pycon

    from sportmonk.soccer import SoccerApiV2
    soccer = SoccerApiV2(api_token='My API token')

    fixtures = soccer.fixtures_today(include=('localTeam', 'visitorTeam'))
    for fixture in fixtures:
        print(fixture['localTeam']['name'], 'plays at home against', fixture['visitorTeam']['name'])

Full documentation is at INSERT LINK HERE.


Convenience & trade-offs
========================

Convenient usage was a key design principle when developing this package. This convenience does not come for free, some
trade-offs had to be made:
- Data is unnested automatically: the contents of `data` are moved to the same level as `data` and `data` by then being
empty and redundant is dropped. As a consequence, the SportMonks-documented response schema differs from the responses
returned by this package.
- All pages of a paginated response are fetched automatically. Fetching all pages is arguably the most common scenario.
The resulting trade-off is that all pages are fetched even when fewer pages suffice.
- Lookups of SportMonks objects by ID are cached. As a result only the fist lookup leads to HTTP traffic. Subsequent
lookups of same SportMonks object use the cache. Here, we think that if you are performing lookups, you are typically
doing a lot of them (e.g. looking up all 100+ bookmakers, seasons, countries, etc.) and so it makes sense to cache to
avoid excessive HTTP requests. The trade-off here is that the first lookup will take much longer than subsequent
lookups.


Installation
============

.. code-block:: pycon

    pip install sportmonks


API Peculiarities
=================

- For some reason when requesting country USA with the continent include, no continent is returned: (E.g.:
  `usa = soccer.country(14566636, include=('continent',))`

- Querying API for all countries returns also non-countries like Europe. I guess this is because of bad data model.

- Querying API for all countries returns a list of countries with a country that is just a new line with some
  whitespace: '\n    '.

- SportMonks returns all countries with two 'Europe' countries: one with ID 41 and another one with ID 8151924. The
  Europe with ID 41 has a continent associated with it, while Europe with ID 8151924 has no continent associated with it.

- The seasons endpoint does not return a fixtures include even though it is listed as an include at
  https://www.sportmonks.com/products/soccer/docs/2.0/seasons/17

- Fixtures with IDs 1625081, 1625092, 1625093, 1625094, 1625095, 1625096, 1625097, 1625098, 1625099, 1625100, 1625101,
  1625102, 1625103, 1625104, 1625105, and 1625144 have no localCoach and visitorCoach includes.

- The standings endpoint does not return any of the available includes.

- If a requested include is unavailable, than it is not returned at all. It would better if it is returned as None. This
  avoids key errors and makes it clear that the requested include is unavailable. An include should be absent only if it
  was not requested.

- The topscorers endpoint returns a reply with three collections: cardscorers, goalscorers, and assistscorers. This is
  an akward data model. Ideally the topscorers endpoint would be broken down into three endpoints: top_goal_scorers,
  top_assist_providers, and top_card_receivers.

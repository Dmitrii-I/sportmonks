"""The `soccer` module implements the `SportMonks soccer HTTP API v2.0.
<https://www.sportmonks.com/sports/soccer/documentation>`__
"""

from os.path import join
from logging import getLogger
from typing import Dict, List, Iterable, Any, Optional
from datetime import date
from requests import get
from sportmonks_v2 import _base
from sportmonks_v2._types import Response, Includes

log = getLogger(__name__)


class SoccerApiV2(_base.BaseApiV2):
    """The ``SoccerApiV2`` class provides SportMonks soccer API client."""

    def __init__(self, api_token: str) -> None:
        """Parameter ``api_token`` is the API token from the SportMonks profile web page."""
        log.info('Initialize soccer API client')
        super().__init__(base_url='https://soccer.sportmonks.com/api/v2.0', api_token=api_token)
        log.info('Client initialized, metadata=%s', self.meta())

    def meta(self) -> Dict[str, Any]:
        """Return meta data that includes your SportMonks plan, subscription, and available sports."""
        # Meta data does not have a dedicated endpoint. Use a data endpoint with fast response and extract meta from its
        # response.
        url = join(self.base_url, 'continents')
        log.info('Fetch metadata')
        raw_response = get(url=url, params=self._base_params, headers=self._base_headers)
        response = raw_response.json()
        try:
            return response['meta']
        except KeyError:
            return response

    def all_endpoints(self) -> Response:
        """Return all available endpoints.
        ``api/v2.0``
        """
        raw_response = get(url=self.base_url, params=self._base_params, headers=self._base_headers)
        response = raw_response.json()

        try:
            return response[self.base_url.split('.com/')[1]]
        except KeyError:
            return response

    def healthcheck(self) -> str:
        """Return the SportMonks soccer API healthcheck.
        ``api/v2.0/healthcheck``

        If it returns `Ok!`, the API is up-and-running.
        """
        url = join(self.base_url, 'healthcheck')
        log.info('Fetch healthcheck')
        raw_response = get(url=url, params=self._base_params, headers=self._base_headers)
        return raw_response.json()

    def all_continents(self, includes: Includes = None) -> Response:
        """Return all continents.
        ``api/v2.0/continents``

        Parameter ``includes`` specifies objects to include in the response. Maximum level of nested includes is 3.
        Valid objects are: `countries`.
        """
        log.info('Fetch all continents, includes=%s', includes)
        continents = self._http_get(endpoint='continents', includes=includes)
        log.info('Fetched %s continents', len(continents))
        return continents

    def continent_by_id(self, continent_id: int, includes: Includes = None) -> Response:
        """Return a continent.
        ``api/v2.0/continents/{id}``

        Parameter ``includes`` specifies objects to include in the response. Maximum level of nested includes is 3.
        Valid objects are: `countries`.
        """
        log.info('Fetch continent (id=%s), includes=%s', continent_id, includes)
        return self._http_get(endpoint=join('continents', str(continent_id)), includes=includes)

    def all_countries(self, includes: Includes = None) -> Response:
        """Return all countries.
        ``api/v2.0/countries``

        Parameter ``includes`` specifies objects to include in the response. Maximum level of nested includes is 2.
        Valid objects are: `leagues`, `continent`.
        """
        log.info('Fetch all countries, includes=%s', includes)
        countries = self._http_get(endpoint='countries', includes=includes)
        log.info('Fetched %s countries', len(countries))
        return countries

    def country_by_id(self, country_id: int, includes: Includes = None) -> Response:
        """Return a country.
        ``api/v2.0/countries/{id}``

        Parameter ``includes`` specifies objects to include in the response. Maximum level of nested includes is 2.
        Valid objects are: `continent`, `leagues`.
        """
        log.info('Fetch country (id=%s), includes=%s', country_id, includes)
        return self._http_get(endpoint=join('countries', str(country_id)), includes=includes)

    def all_leagues(self, includes: Includes = None) -> Response:
        """Return all leagues.
        ``api/v2.0/leagues``

        Parameter ``includes`` specifies objects to include in the response. Maximum level of nested includes is 2.
        Valid objects are: `country`, `season`, `seasons`. The `season` include returns current season of the
        league. The `seasons` include Return all seasons of the league, including the current season.
        """
        log.info('Fetch all leagues, includes=%s', includes)
        leagues = self._http_get(endpoint='leagues', includes=includes)
        log.info('Fetched %s leagues', len(leagues))
        return leagues

    def league_by_id(self, league_id: int, includes: Includes = None) -> Response:
        """Return a league.
        ``api/v2.0/leagues/{id}``

        Parameter ``includes`` specifies objects to include in the response. Maximum level of nested includes is 2.
        Valid objects are: `country`, `season`, `seasons`. The `season` include returns current season of the
        league. The `seasons` include returns all seasons of the league, including the current season.
        """
        log.info('Fetch league (id=%s), includes=%s', league_id, includes)
        return self._http_get(endpoint=join('leagues', str(league_id)), includes=includes)

    def all_seasons(self, includes: Includes = None) -> Response:
        """Return all seasons.
        ``api/v2.0/seasons``

        Parameter ``includes`` specifies objects to include in the response. Maximum level of nested includes is 2.
        Valid objects are: `league`, `stages`, `rounds`, `upcoming`, `results`, `groups`, `goalscorers`,
        `cardscorers`, `assistscorers`, `aggregatedGoalscorers`, `aggregatedCardscorers`, `aggregatedAssistscorers`.
        """
        log.info('Fetch all seasons, includes=%s', includes)
        seasons = self._http_get(endpoint='seasons', includes=includes)
        log.info('Fetched %s seasons', len(seasons))
        return seasons

    def season_by_id(self, season_id: int, includes: Includes = None) -> Response:
        """Return a season.
        ``api/v2.0/seasons/{id}``

        Parameter ``includes`` specifies objects to include in the response. Maximum level of nested includes is 2.
        Valid objects are: `league`, `stages`, `rounds`, `upcoming`, `results`, `groups`, `goalscorers`,
        `cardscorers`, `assistscorers`, `aggregatedGoalscorers`, `aggregatedCardscorers`, `aggregatedAssistscorers`.
        """
        log.info('Fetch season (id=%s), includes=%s', season_id, includes)
        return self._http_get(endpoint=join('seasons', str(season_id)), includes=includes)

    def fixture_by_id(self, fixture_id: int, includes: Includes = None, market_ids: Optional[List[int]] = None,
                      bookmaker_ids: Optional[List[int]] = None) -> Response:
        """Return a fixture.
        ``api/v2.0/fixtures/{id}``

        Parameter ``includes`` specifies objects to include in the response. Maximum level of nested includes is 10.
        Valid objects are: `localTeam`, `visitorTeam`, `substitutions`, `goals`, `cards`, `other`, `events`, `corners`,
        `lineup`, `bench`, `sidelined`, `stats`, `comments`, `tvstations`, `highlights`, `league`, `season`,
        `round`, `stage`, `referee`, `venue`, `odds`, `inplayOdds`, `flatOdds`, `inplay`, `localCoach`,
        `visitorCoach`, `group`, `trends`, `firstAssistant`, `secondAssistant`, `fourthOfficial`, `shootout`.

        Parameter ``market_ids`` specifies markets from which the fixtures will be returned, defaulting to all markets.

        Parameter ``bookmaker_ids`` specifies bookmakers from which the fixtures will be returned,
        defaulting to all bookmakers.
        """
        log.info('Fetch fixture (id=%s), includes=%s', fixture_id, includes)
        return self._http_get(endpoint=join('fixtures', str(fixture_id)), includes=includes,
                              params={'markets': market_ids or [], 'bookmakers': bookmaker_ids or []})

    def fixtures_at(self, at_date: date, includes: Includes = None, market_ids: Optional[List[int]] = None,
                    bookmaker_ids: Optional[List[int]] = None) -> Response:
        """Return fixtures at ``date``. The date is inclusive.
        ``api/v2.0/fixtures/date/{date}``

        Parameter ``includes`` specifies objects to include in the response. Maximum level of nested includes is 10.
        Valid objects are: `localTeam`, `visitorTeam`, `substitutions`, `goals`, `cards`, `other`, `events`, `corners`,
        `lineup`, `bench`, `sidelined`, `stats`, `comments`, `tvstations`, `highlights`, `league`, `season`,
        `round`, `stage`, `referee`, `venue`, `odds`, `inplayOdds`, `flatOdds`, `inplay`, `localCoach`,
        `visitorCoach`, `group`, `trends`, `firstAssistant`, `secondAssistant`, `fourthOfficial`, `shootout`.

        Parameter ``market_ids`` specifies markets from which the fixtures will be returned, defaulting to all markets.

        Parameter ``bookmaker_ids`` specifies bookmakers from which the fixtures will be returned,
        defaulting to all bookmakers.
        """
        endpoint = join('fixtures', at_date.strftime('%Y-%m-%d'))
        log.info('Fetch fixtures, at=%s, includes=%s, market ids=%s, bookmaker ids=%s', at_date, includes,
                 market_ids or 'all markets', bookmaker_ids or 'all bookmakers')
        fixtures = self._http_get(endpoint=endpoint, includes=includes, params={'markets': market_ids or [],
                                                                                'bookmakers': bookmaker_ids or []})
        log.info('Fetched %s fixtures', len(fixtures))
        return fixtures

    def fixtures_between(self, start_date: date, end_date: date, includes: Includes = None,
                         league_ids: Optional[List[int]] = None, market_ids: Optional[List[int]] = None,
                         bookmaker_ids: Optional[List[int]] = None) -> Response:
        """Return fixtures between ``start_date`` and ``end_date``. The dates are inclusive.
        ``api/v2.0/fixtures/between/{from}/{to}``

        Parameter ``includes`` specifies objects to include in the response. Maximum level of nested includes is 10.
        Valid objects are: `localTeam`, `visitorTeam`, `substitutions`, `goals`, `cards`, `other`, `events`, `corners`,
        `lineup`, `bench`, `sidelined`, `stats`, `comments`, `tvstations`, `highlights`, `league`, `season`,
        `round`, `stage`, `referee`, `venue`, `odds`, `inplayOdds`, `flatOdds`, `inplay`, `localCoach`,
        `visitorCoach`, `group`, `trends`, `firstAssistant`, `secondAssistant`, `fourthOfficial`, `shootout`.

        Parameter ``league_ids`` specifies leagues from which the fixtures will be returned, defaulting to all leagues.

        Parameter ``market_ids`` specifies markets from which the fixtures will be returned, defaulting to all markets.

        Parameter ``bookmaker_ids`` specifies bookmakers from which the fixtures will be returned,
        defaulting to all bookmakers.
        """
        endpoint = join('fixtures', 'between', start_date.strftime('%Y-%m-%d'), end_date.strftime('%Y-%m-%d'))
        log.info('Fetch fixtures, from=%s, until=%s, league ids=%s, market ids=%s, bookmaker ids=%s, includes=%s',
                 start_date, end_date, league_ids or 'all leagues', market_ids or 'all markets', bookmaker_ids or
                 'all bookmakers', includes)
        fixtures = self._http_get(endpoint=endpoint, includes=includes, params={'leagues': league_ids or [],
                                                                                'markets': market_ids or [],
                                                                                'bookmakers': bookmaker_ids or []})
        log.info('Fetched %s fixtures', len(fixtures))
        return fixtures

    def fixtures_between_by_team_id(self, start_date: date, end_date: date, team_id: int, includes: Includes = None,
                                    league_ids: Optional[List[int]] = None, market_ids: Optional[List[int]] = None,
                                    bookmaker_ids: Optional[List[int]] = None) -> Response:
        """Return fixtures between ``start_date`` and ``end_date`` for a team specified by ``team_id``.
        ``api/v2.0/fixtures/between/{from}/{to}/{team}``

        Parameter ``includes`` specifies objects to include in the response. Maximum level of nested includes is 3.
        Valid objects are: `localTeam`, `visitorTeam`, `substitutions`, `goals`, `cards`, `other`, `events`, `corners`,
        `lineup`, `bench`, `sidelined`, `stats`, `comments`, `tvstations`, `highlights`, `league`, `season`,
        `round`, `stage`, `referee`, `venue`, `odds`, `inplayOdds`, `flatOdds`, `inplay`, `localCoach`,
        `visitorCoach`, `group`, `trends`, `firstAssistant`, `secondAssistant`, `fourthOfficial`, `shootout`.

        Parameter ``league_ids`` specifies leagues from which the fixtures will be returned, defaulting to all leagues.

        Parameter ``market_ids`` specifies markets from which the fixtures will be returned, defaulting to all markets.

        Parameter ``bookmaker_ids`` specifies bookmakers from which the fixtures will be returned,
        defaulting to all bookmakers.
        """
        endpoint = join('fixtures', 'between', start_date.strftime('%Y-%m-%d'), end_date.strftime('%Y-%m-%d'),
                        str(team_id))
        log.info('Fetch fixtures of a team (id=%s), from=%s, until=%s, league ids=%s, market ids=%s, bookmaker ids=%s,'
                 ' includes=%s', team_id, start_date, end_date, league_ids or 'all leagues',
                 market_ids or 'all markets', bookmaker_ids or 'all bookmakers', includes)
        team_fixtures = self._http_get(endpoint=endpoint, includes=includes, params={'leagues': league_ids or [],
                                                                                     'markets': market_ids or [],
                                                                                     'bookmakers': bookmaker_ids or []})
        log.info('Fetched %s team fixtures', len(team_fixtures))
        return team_fixtures

    def fixtures_between_by_season_id(self, start_date: date, end_date: date, season_id: int, includes: Includes = None,
                                      league_ids: Optional[List[int]] = None, market_ids: Optional[List[int]] = None,
                                      bookmaker_ids: Optional[List[int]] = None) -> Response:
        """Return fixtures between ``start_date`` and ``end_date`` for a season specified by ``season_id``.
        ``api/v2.0/fixtures/season/{id}/between/{from}/{to}``

        Parameter ``includes`` specifies objects to include in the response. Maximum level of nested includes is 3.
        Valid objects are: `localTeam`, `visitorTeam`, `substitutions`, `goals`, `cards`, `other`, `events`, `corners`,
        `lineup`, `bench`, `sidelined`, `stats`, `comments`, `tvstations`, `highlights`, `league`, `season`,
        `round`, `stage`, `referee`, `venue`, `odds`, `inplayOdds`, `flatOdds`, `inplay`, `localCoach`,
        `visitorCoach`, `group`, `trends`, `firstAssistant`, `secondAssistant`, `fourthOfficial`, `shootout`.

        Parameter ``league_ids`` specifies leagues from which the fixtures will be returned, defaulting to all leagues.

        Parameter ``market_ids`` specifies markets from which the fixtures will be returned, defaulting to all markets.

        Parameter ``bookmaker_ids`` specifies bookmakers from which the fixtures will be returned,
        defaulting to all bookmakers.
        """
        endpoint = join('fixtures', 'season', str(season_id), 'between', start_date.strftime('%Y-%m-%d'),
                        end_date.strftime('%Y-%m-d'))
        log.info('Fetch fixtures of a season (id=%s), from=%s, until=%s, league ids=%s, market ids=%s, '
                 'bookmaker ids=%s, includes=%s', season_id, start_date, end_date, league_ids or 'all leagues',
                 market_ids or 'all markets', bookmaker_ids or 'all bookmakers', includes)
        season_fixtures = self._http_get(endpoint=endpoint, includes=includes,
                                         params={'leagues': league_ids or [], 'markets': market_ids or [],
                                                 'bookmakers': bookmaker_ids or []})

        return season_fixtures

    def fixtures_by_multiple_ids(self, fixture_ids: Iterable[int], includes: Includes = None,
                                 league_ids: Optional[List[int]] = None, market_ids: Optional[List[int]] = None,
                                 bookmaker_ids: Optional[List[int]] = None) -> Response:
        """Return multiple fixtures.
        ``api/v2.0/fixtures/multi/{ids}``

        Parameter ``includes`` specifies objects to include in the response. Maximum level of nested includes is 10.
        Valid objects are: `localTeam`, `visitorTeam`, `substitutions`, `goals`, `cards`, `other`, `events`, `corners`,
        `lineup`, `bench`, `sidelined`, `stats`, `comments`, `tvstations`, `highlights`, `league`, `season`,
        `round`, `stage`, `referee`, `venue`, `odds`, `inplayOdds`, `flatOdds`, `inplay`, `localCoach`,
        `visitorCoach`, `group`, `trends`, `firstAssistant`, `secondAssistant`, `fourthOfficial`, `shootout`.

        Parameter ``league_ids`` specifies leagues from which the fixtures will be returned, defaulting to all leagues.

        Parameter ``market_ids`` specifies markets from which the fixtures will be returned, defaulting to all markets.

        Parameter ``bookmaker_ids`` specifies bookmakers from which the fixtures will be returned,
        defaulting to all bookmakers.
        """
        fixture_ids = list(fixture_ids)
        endpoint = join('fixtures', 'multi', ','.join(str(fixture_id) for fixture_id in fixture_ids))
        log.info('Fetch fixtures (id=%s), league ids=%s, market ids=%s, '
                 'bookmaker ids=%s, includes=%s', fixture_ids, league_ids or 'all leagues',
                 market_ids or 'all markets', bookmaker_ids or 'all bookmakers', includes)
        return self._http_get(endpoint=endpoint, includes=includes, params={'leagues': league_ids or [],
                                                                            'markets': market_ids or [],
                                                                            'bookmakers': bookmaker_ids or []})

    def fixtures_today(self, includes: Includes = None, league_ids: Optional[List[int]] = None,
                       market_ids: Optional[List[int]] = None, bookmaker_ids: Optional[List[int]] = None) -> Response:
        """Return today's fixtures, played and to be played.
        ``api/v2.0/livescores``

        Parameter ``includes`` specifies objects to include in the response. Maximum level of nested includes is 10.
        Valid objects are: `localTeam`, `visitorTeam`, `substitutions`, `goals`, `cards`, `other`, `events`, `corners`,
        `lineup`, `bench`, `sidelined`, `stats`, `comments`, `tvstations`, `highlights`, `league`, `season`,
        `round`, `stage`, `referee`, `venue`, `odds`, `inplayOdds`, `flatOdds`, `inplay`, `localCoach`,
        `visitorCoach`, `group`, `trends`, `firstAssistant`, `secondAssistant`, `fourthOfficial`, `shootout`.

        Parameter ``league_ids`` specifies leagues from which the fixtures will be returned, defaulting to all leagues.

        Parameter ``market_ids`` specifies markets from which the fixtures will be returned, defaulting to all markets.

        Parameter ``bookmaker_ids`` specifies bookmakers from which the fixtures will be returned,
        defaulting to all bookmakers.
        """
        log.info('Fetch today\'s fixtures, league ids=%s, market ids=%s, bookmaker ids=%s includes=%s',
                 league_ids or 'all leagues', market_ids or 'all markets', bookmaker_ids or 'all bookmakers', includes)
        fixtures_today = self._http_get(endpoint='livescores', includes=includes,
                                        params={'leagues': league_ids or [], 'markets': market_ids or [],
                                                'bookmakers': bookmaker_ids or []})
        log.info('Fetched %s fixtures', len(fixtures_today))
        return fixtures_today

    def fixtures_in_play(self, includes: Includes = None, league_ids: Optional[List[int]] = None,
                         market_ids: Optional[List[int]] = None, bookmaker_ids: Optional[List[int]] = None) -> Response:
        """Return in-play fixtures.
        ``api/v2.0/livescores/now``

        Note that in-play is defined by SportMonks as fixtures currently played, plus fixtures that will begin within
        45 minutes, and fixtures that ended less than 30 minutes ago.

        Parameter ``includes`` specifies objects to include in the response. Maximum level of nested includes is 10.
        Valid objects are: `localTeam`, `visitorTeam`, `substitutions`, `goals`, `cards`, `other`, `events`, `corners`,
        `lineup`, `bench`, `sidelined`, `stats`, `comments`, `tvstations`, `highlights`, `league`, `season`,
        `round`, `stage`, `referee`, `venue`, `odds`, `inplayOdds`, `flatOdds`, `inplay`, `localCoach`,
        `visitorCoach`, `group`, `trends`, `firstAssistant`, `secondAssistant`, `fourthOfficial`, `shootout`.

        Parameter ``league_ids`` specifies leagues from which the fixtures will be returned, defaulting to all leagues.

        Parameter ``market_ids`` specifies markets from which the fixtures will be returned, defaulting to all markets.

        Parameter ``bookmaker_ids`` specifies bookmakers from which the fixtures will be returned,
        defaulting to all bookmakers.
        """
        log.info('Fetch fixtures in play, league ids=%s, market ids=%s, bookmaker ids=%s includes=%s',
                 league_ids or 'all leagues', market_ids or 'all markets', bookmaker_ids or 'all bookmakers', includes)
        endpoint = join('livescores', 'now')
        fixtures_in_play = self._http_get(endpoint=endpoint, includes=includes,
                                          params={'leagues': league_ids or [], 'markets': market_ids or [],
                                                  'bookmakers': bookmaker_ids or []})
        log.info('Fetched %s fixtures in play', len(fixtures_in_play))
        return fixtures_in_play

    def commentaries_by_fixture_id(self, fixture_id: int) -> Response:
        """Return commentaries of a fixture.
        ``api/v2.0/commentaries/fixture/{id}``

        Not all fixtures have commentaries. If a fixture has no commentaries then an empty list is returned.
        """
        log.info('Fetch commentaries of a fixture (id=%s)', fixture_id)
        commentaries = self._http_get(endpoint=join('commentaries', 'fixture', str(fixture_id)))
        log.info('Fetched %s commentaries', len(commentaries))
        return commentaries

    def all_video_highlights(self, includes: Includes = None) -> Response:
        """Return links to video highlights of all fixtures or of a fixture specified by ``fixture_id``.
        ``api/v2.0/highlights``

        Parameter ``includes`` specifies objects to include in the response. Maximum level of nested includes is 2.
        Valid objects are: `fixture`.
        """
        log.info('Fetch video highlights of all fixtures, includes=%s', includes)
        video_highlights = self._http_get(endpoint='highlights', includes=includes)
        log.info('Fetched %s video highlights', len(video_highlights))
        return video_highlights

    def video_highlights_by_fixture_id(self, fixture_id: int, includes: Includes = None) -> Response:
        """Return links to video highlights of all fixtures or of a fixture specified by ``fixture_id``.
        ``api/v2.0/highlights/fixture/{id}``

        Parameter ``includes`` specifies objects to include in the response. Maximum level of nested includes is 2.
        Valid objects are: `fixture`.
        """
        log.info('Fetch video highlights of a fixture (id=%s), includes=%s', fixture_id, includes)
        video_highlights = self._http_get(endpoint=join('highlights', 'fixture', str(fixture_id)), includes=includes)
        log.info('Fetched %s video highlights', len(video_highlights))
        return video_highlights

    def head_to_head_by_team_ids(self, team_ids: Iterable[int], includes: Includes = None) -> Response:
        """Return all head-to-head fixtures of two teams specified by ``team_ids``.
        ``api/v2.0/head2head/{team_id_1}/{team_id_2}``

        Parameter ``includes`` specifies objects to include in the response. Maximum level of nested includes is 2.
        Valid objects are:	`localTeam`, `visitorTeam`, `substitutions`, `goals`, `cards`, `other`, `lineup`, `bench`,
        `stats`, `comments`, `tvstations`, `highlights`, `league`, `season`, `round`, `stage`, `referee`, `events`,
        `venue`, `trends`.
        """
        team_ids = list(team_ids)
        endpoint = join('head2head', str(team_ids[0]), str(team_ids[1]))
        log.info('Fetch head-to-head fixtures of two teams (ids=%s), includes=%s', team_ids, includes)
        head_to_head_fixtures = self._http_get(endpoint=endpoint, includes=includes)
        log.info('Fetch fixtures (id=%s), includes=%s', team_ids, includes)
        return head_to_head_fixtures

    def standings_by_season_id(self, season_id: int, group_id: Optional[int] = None,
                               includes: Includes = None) -> Response:
        """Return standings of a season.
        ``api/v2.0/standings/season/{id}``

        Parameter ``group_id`` specifies for which group to return the standings. Groups are found in tournaments like
        the FIFA World Cup (e.g. Group A has group ID 185).

        Parameter ``includes`` specifies objects to include in the response. Maximum level of nested includes is 2.
        Valid objects are: `team`, `league`, `season`, `round`, `stage`.
        """
        includes = ['standings.' + inc for inc in includes or []]
        endpoint = join('standings', 'season', str(season_id))

        log.info('Fetch standings, season id=%s, group id=%s, includes=%s', season_id, group_id or 'all groups',
                 includes)
        standings = self._http_get(endpoint=endpoint, includes=includes, params={'group_id': group_id})
        log.info('Fetched %s standings', len(standings))
        return standings

    def live_standings_by_season_id(self, season_id: int, group_id: Optional[int] = None,
                                    includes: Includes = None) -> Response:
        """Return live standings of a season.
        ``api/v2.0/standings/season/{id}``

        Parameter ``group_id`` specifies for which group to return the standings. Groups are found in tournaments like
        the FIFA World Cup (e.g. Group A has group ID 185).

        Parameter ``includes`` specifies objects to include in the response. Maximum level of nested includes is 2.
        Valid objects are: `team`, `league`, `season`, `round`, `stage`.
        """
        includes = ['standings.' + inc for inc in includes or []]
        endpoint = join('standings', 'season', 'live', str(season_id))

        log.info('Fetch live standings, season id=%s, group id=%s, includes=%s', season_id, group_id or 'all groups',
                 includes)
        live_standings = self._http_get(endpoint=endpoint, includes=includes, params={'group_id': group_id})
        log.info('Fetched %s live standings', len(live_standings))
        return live_standings

    def team_by_id(self, team_id: int, includes: Includes = None) -> Response:
        """Return a team.
        ``api/v2.0/teams/{id}``

        Parameter ``includes`` specifies objects to include in the response. Maximum level of nested includes is 3.
        Valid objects are: `country`, `squad`, `coach`, `transfers`, `sidelined`, `stats`, `venue`, `fifaranking`,
        `uefaranking`, `visitorFixtures`, `localFixtures`, `visitorResults`, `localResults`, `latest`, `upcoming`.
        """
        log.info('Fetch team (id=%s), includes=%s', team_id, includes)
        return self._http_get(endpoint=join('teams', str(team_id)), includes=includes)

    # TODO: def legacy_team_by_id(self) -> Response:
    # """
    # ``api/v2.0/legacy/teams/{id}``
    # """

    def teams_by_season_id(self, season_id: int, includes: Includes = None) -> Response:
        """Return all teams that played during a season.
        ``api/v2.0/teams/season/{season_id}``

        Parameter ``includes`` specifies objects to include in the response. Maximum level of nested includes is 3.
        Valid objects are: `country`, `squad`, `coach`, `transfers`, `sidelined`, `stats`, `venue`, `fifaranking`,
        `uefaranking`, `visitorFixtures`, `localFixtures`, `visitorResults`, `localResults`, `latest`, `upcoming`.
        """
        log.info('Fetch teams of a season (id=%s), includes=%s', season_id, includes)
        teams = self._http_get(endpoint=join('teams', 'season', str(season_id)), includes=includes)
        log.info('Fetched %s teams', len(teams))
        return teams

    def player_by_id(self, player_id: int, includes: Includes = None) -> Response:
        """Return a player.
        ``api/v2.0/players/{id}``

        Parameter ``includes`` specifies objects to include in the response. Maximum level of nested includes is 2.
        Valid objects are: `position`, `team`, `stats`, `trophies`, `sidelined`, `transfers`, `lineups`.
        """
        log.info('Fetch player (id=%s), includes=%s', player_id, includes)
        return self._http_get(endpoint=join('players', str(player_id)), includes=includes)

    # TODO: includes = ['goalscorers.' + inc for inc in includes or []] etc.
    def topscorers_by_season_id(self, season_id: int, includes: Includes = None) -> Response:
        """Return top scorers of a season.
        ``api/v2.0/topscorers/season/{id}``

        Three types of top scorers are returned: most goals, most assists, and most cards.

        Parameter ``includes`` specifies objects to include in the response. Maximum level of nested includes is 3.
        Valid objects are: `goalscorers.player`, `goalscorers.team` `cardscorers.player`, `cardscorers.team`,
        `assistscorers.player`, `assistscorers.team`.
        """
        endpoint = join('topscorers', 'season', str(season_id))
        log.info('Fetch top scorers of a season (id=%s), includes=%s', season_id, includes)
        return self._http_get(endpoint=endpoint, includes=includes)

    # TODO: def aggregated_topscorers_by_season_id(self): -> Response:
    # """
    # ``api/v2.0/topscorers/season/{id}/aggregated``
    # """

    def venue_by_id(self, venue_id: int) -> Response:
        """Return a venue.
        ``api/v2.0/venues/{id}``
        """
        log.info('Fetch venue (id=%s)', venue_id)
        return self._http_get(endpoint=join('venues', str(venue_id)))

    def venues_by_season_id(self, season_id: int) -> Response:
        """Return venues of specified season.
        ``api/v2.0/venues/season/{id}``
        """
        log.info('Fetch venues of a season (id=%s)', season_id)
        season_venues = self._http_get(endpoint=join('venues', 'season', str(season_id)))
        log.info('Fetched %s venues of a season', len(season_venues))
        return season_venues

    def round_by_id(self, round_id: int, includes: Includes = None) -> Response:
        """Return a round.
        ``api/v2.0/rounds/{id}``

        Parameter ``includes`` specifies objects to include in the response. Maximum level of nested includes is 2.
        Valid objects are: `fixtures`, `results`, `season`, `league`.
        """
        log.info('Fetch round (id=%s), includes=%s', round_id, includes)
        return self._http_get(endpoint=join('rounds', str(round_id)), includes=includes)

    def rounds_by_season_id(self, season_id: int, includes: Includes = None) -> Response:
        """Return rounds of a season.
        ``api/v2.0/rounds/season/{id}``

        Parameter ``includes`` specifies objects to include in the response. Maximum level of nested includes is 2.
        Valid objects are: `fixtures`, `results`, `season`, `league`.
        """
        log.info('Fetch rounds of a season (id=%s), includes=%s', season_id, includes)
        rounds = self._http_get(endpoint=join('rounds', 'season', str(season_id)), includes=includes)
        log.info('Fetched %s rounds', len(rounds))
        return rounds

    def pre_match_odds(self, fixture_id: int, bookmaker_id: Optional[int] = None,
                       market_id: Optional[int] = None) -> Response:
        """Return pre-match odds of a fixture."""
        if bookmaker_id:
            endpoint = join('odds', 'fixture', str(fixture_id), 'bookmaker', str(bookmaker_id))
            log.info('Fetch pre-match, fixture id=%s, bookmaker id=%s', fixture_id, bookmaker_id)
        elif market_id:
            endpoint = join('odds', 'fixture', str(fixture_id), 'market', str(market_id))
            log.info('Fetch pre-match, fixture id=%s, market id=%s', fixture_id, market_id)
        else:
            endpoint = join('odds', 'fixture', str(fixture_id))

        pre_match_odds = self._http_get(endpoint=endpoint)
        log.info('Fetched %s pre-match odds', len(pre_match_odds))
        return pre_match_odds

    def in_play_odds(self, fixture_id: Optional[int]) -> Response:
        """Return in-play odds of a fixture."""
        if fixture_id:
            log.info('Fetch in-play odds, fixture id=%s', fixture_id)
            endpoint = join('odds', 'inplay', 'fixture', str(fixture_id))
        else:
            log.info('Fetch in-play odds')
            endpoint = join('odds', 'inplay', 'live')
        in_play_odds = self._http_get(endpoint=endpoint)
        log.info('Fetched %s in-play odds', len(in_play_odds))
        return in_play_odds

    # TODO: split pre_match_odds and in_play_odds to:

    # def odds_by_fixture_and_bookmaker_id(self) -> Response:
    #   """
    #   ``api/v2.0/odds/fixture/{id}/bookmaker/{bookmaker_id}``
    #   """
    #
    # def odds_by_fixture_and_market_id(self) -> Response:
    #   """
    #   ``api/v2.0/odds/fixture/{id}/market/{market_id}``
    #   """
    #
    # def odds_by_fixture_id(self) -> Response:
    #   """
    #   ``api/v2.0/odds/fixture/{id}``
    #   """
    #
    # def inplay_odds(self) -> Response:
    #   """
    #   ``api/v2.0/odds/inplay/live``
    #   """
    #
    # def inplay_odds_by_fixture_id(self) -> Response:
    #   """
    #   ``api/v2.0/odds/inplay/fixture/{id}``
    #   """

    def coach_by_id(self, coach_id: int) -> Response:
        """Return a coach.
        ``api/v2.0/coaches/{id}``
        """
        log.info('Fetch coach (id=%s)', coach_id)
        return self._http_get(endpoint=join('coaches', str(coach_id)))

    def stage_by_id(self, stage_id: int, includes: Includes = None) -> Response:
        """Return a stage.
        ``api/v2.0/stages/{id}``

        Parameter ``includes`` specifies objects to include in the response. Maximum level of nested includes is 2.
        Valid objects are: `fixtures`, `results`, `season`, `league`.
        """
        log.info('Fetch stage (id=%s), includes=%s', stage_id, includes)
        return self._http_get(endpoint=join('stages', str(stage_id)), includes=includes)

    def stages_by_season_id(self, season_id: int, includes: Includes = None) -> Response:
        """Return stages of a season.
        ``api/v2.0/stages/season/{id}``

        Parameter ``includes`` specifies objects to include in the response. Maximum level of nested includes is 2.
        Valid objects are: `fixtures`, `results`, `season`, `league`.
        """
        log.info('Fetch stages of a season (id=%s), includes=%s', season_id, includes)
        stages = self._http_get(endpoint=join('stages', 'season', str(season_id)), includes=includes)
        log.info('Fetched %s stages', len(stages))
        return stages

    def all_bookmakers(self) -> Response:
        """Return all bookmakers.
        ``api/v2.0/bookmakers``
        """
        log.info('Fetch all bookmakers')
        bookmakers = self._http_get(endpoint='bookmakers')
        log.info('Fetched %s bookmakers', len(bookmakers))
        return bookmakers

    def bookmaker_by_id(self, bookmaker_id: int) -> Response:
        """Return a bookmaker.
        ``api/v2.0/bookmakers/{id}``
        """
        log.info('Fetch bookmaker (id=%s)', bookmaker_id)
        return self._http_get(endpoint=join('bookmakers', str(bookmaker_id)))

    def all_markets(self) -> Response:
        """Return all betting markets, e.g. '3Way Result', 'Home/Away'.
        ``api/v2.0/markets``
        """
        log.info('Fetch all markets')
        markets = self._http_get(endpoint='markets')
        log.info('Fetched %s markets', len(markets))
        return markets

    def market_by_id(self, market_id: int) -> Response:
        """Return a market.
        ``api/v2.0/markets/{id}``
        """
        log.info('Fetch market (id=%s)', market_id)
        return self._http_get(endpoint=join('markets', str(market_id)))

    def season_results(self, season_id: int, includes: Includes = None) -> Response:
        """Return completed fixtures of a season.
        ``api/v2.0/seasons/result/{id}``

        Parameter ``includes`` specifies objects to include in the response. Maximum level of nested includes is 1.
        Valid objects are: `localTeam`, `visitorTeam`, `substitutions`, `goals`, `cards`, `other`, `corners`,
        `lineup`, `bench`, `sidelined`, `stats`, `comments`, `tvstations`, `highlights`, `league`, `season`, `round`,
        `stage`, `referee`, `events`, `venue`, `odds`, `flatOdds`, `inplay`, `localCoach`, `visitorCoach`, `group`,
        `trends`.
        """
        includes = ['results'] + ['results.' + inc for inc in includes or []]
        print(includes)

        log.info('Fetch results of a season (id=%s), includes=%s', season_id, includes)

        season_results = self.season_by_id(season_id=season_id, includes=includes)

        if isinstance(season_results, dict):
            season_results = season_results['results']
        else:
            raise TypeError('Expected `dict`, got `%s`' % type(season_results))

        log.info('Fetched %s results', len(season_results))
        return season_results

    def squad_by_season_and_team_id(self, season_id: int, team_id: int, includes: Includes = None) -> Response:
        """Return a squad. A squad is a set of players that played for a team during a season.
        ``api/v2.0/squad/season/{id}/team/{team_id}``

        Parameter ``includes`` specifies objects to include in the response. Maximum level of nested includes is 3.
        Valid objects are: `player`, `position`.
        """
        log.info('Fetch squad of a team (id=%s) during a season (id=%s), includes=%s', team_id, season_id, includes)
        squad = self._http_get(endpoint=join('squad', 'season', str(season_id), 'team', str(team_id)),
                               includes=includes)
        log.info('Fetched %s squad players', len(squad))
        return squad

    def tv_stations_by_fixture_id(self, fixture_id: int) -> Response:
        """Return tv stations broadcasting specified fixture.
        ``api/v2.0/tvstations/fixture/{id}``
        """
        log.info('Fetch TV stations broadcasting a fixture (id=%s)', fixture_id)
        fixture_tv_stations = self._http_get(endpoint=join('tvstations', 'fixture', str(fixture_id)))
        log.info('Fetched %s TV stations', len(fixture_tv_stations))
        return fixture_tv_stations

    def team_stats(self, team_id: int) -> Response:
        """Return stats of a team."""
        log.info('Fetch stats of a team (id=%s)', team_id)
        team_stats = self._http_get(endpoint=join('teams', str(team_id)), includes=['stats'])
        if isinstance(team_stats, dict):
            return team_stats['stats']
        else:
            raise TypeError('Expected `dict`, got `%s`' % type(team_stats))

    # TODO: implement endpoints
    # def season_stats(self, season_id: int) -> Response:
    # def fixture_trends(self, fixture_id: int) -> Response:
    # def team_squad(self, team_id: int) -> Response:
    # def player_injuries(self, player_id: int) -> Response:
    # def player_transfers(self, player_id: int) -> Response:
    # def referee_by_id(self, referee_id: int) -> Response:
    #   """
    #   ``api/v2.0/referees/{id}``
    #   """


""" The `soccer` module implements the `SportMonks soccer HTTP API v2.0
<https://www.sportmonks.com/sports/soccer/documentation>`_.
"""


from os.path import join
from logging import getLogger
from typing import Dict, List
from datetime import date
from sportmonks import base
from requests import get


log = getLogger(__name__)


class SoccerApiV2(base.BaseApiV2):
    """ The ``SoccerApiV2`` class provides SportMonks soccer API client. """

    def __init__(self, api_token: str):
        """ Parameter ``api_token`` is the API token from the SportMonks profile web page. """

        super().__init__(base_url='https://soccer.sportmonks.com/api/v2.0', api_token=api_token)

    @property
    def _callables_cached_objects(self):
        """ Returns callables of cached SportMonks soccer objects used by ``_lookup_table`` method. """

        return {
            'continent': self.continents,
            'country': self.countries,
            'league': self.leagues,
            'bookmaker': self.bookmakers
        }

    def meta(self):
        """ Returns meta data that includes your SportMonks plan, subscription, and available sports. """

        # Meta data does not have a dedicated endpoint. Use a data endpoint with fast response and extract meta from its
        # response.
        url = join(self.base_url, 'continents')
        raw_response = get(url=url, params=self.base_params, headers=self.base_headers)
        response = raw_response.json()
        return response['meta']

    def bookmaker(self, bookmaker_id: int) -> Dict:
        """ Returns a bookmaker. """

        return self._lookup_table(sportmonks_object='bookmaker')[bookmaker_id]

    def bookmakers(self) -> List[Dict]:
        """ Returns all bookmakers. """

        return self._http_get(endpoint='bookmakers')

    def continent(self, continent_id: int, includes: tuple = None) -> Dict:
        """ Returns a continent.

        Parameter ``includes`` specifies objects to include in the response. Maximum level of includes allowed is 10.
        Valid objects are: `countries`.
        """

        return self._lookup_table(sportmonks_object='continent', includes=includes)[continent_id]

    def continents(self, includes: tuple = None) -> Dict or List[Dict]:
        """ Returns all continents.

        Parameter ``includes`` specifies objects to include in the response. Maximum level of includes allowed is 10.
        Valid objects are: `countries`.
        """

        return self._http_get(endpoint='continents', includes=includes)

    def country(self, country_id: int, includes: tuple = None) -> Dict:
        """ Returns a country.

        Parameter ``includes`` specifies objects to include in the response. Maximum level of includes allowed is 2.
        Valid objects are: `continent`, `leagues`.
        """

        return self._lookup_table(sportmonks_object='country', includes=includes)[country_id]

    def countries(self, includes: tuple = None) -> List[Dict]:
        """ Returns all countries.

        Parameter ``includes`` specifies objects to include in the response. Maximum level of includes allowed is 2.
        Valid objects are: `continent`, `leagues`.
        """

        return self._http_get(endpoint='countries', includes=includes)

    def league(self, league_id: int, includes: tuple = None) -> Dict:
        """ Returns a league.

        Parameter ``includes`` specifies objects to include in the response. Maximum level of includes allowed is 2.
        Valid objects are: `country`, `season`, `seasons`. The `season` include returns current season of the
        league. The `seasons` include returns all seasons of the league, including the current season.
        """

        return self._lookup_table(sportmonks_object='league', includes=includes)[league_id]

    def leagues(self, includes: tuple = None) -> List[Dict]:
        """ Returns all leagues.

        Parameter ``includes`` specifies objects to include in the response. Maximum level of includes allowed is 2.
        Valid objects are: `country`, `season`, `seasons`. The `season` include returns current season of the
        league. The `seasons` include returns all seasons of the league, including the current season.
        """

        return self._http_get(endpoint='leagues', includes=includes)

    def season(self, season_id: int, includes: tuple = None) -> Dict:
        """ Returns a season.

        Parameter ``includes`` specifies objects to include in the response. Maximum level of includes allowed is 10.
        Valid objects are: `league`, `stages`, `rounds`, `fixtures`, `upcoming`, `results`, `groups`.
        """

        return self._http_get(endpoint=join('seasons', str(season_id)), includes=includes)

    def seasons(self, includes: tuple = None) -> List[Dict]:
        """ Returns all seasons.

        Parameter ``includes`` specifies objects to include in the response. Maximum level of includes allowed is 2.
        Valid objects are: `league`, `stages`, `rounds`, `fixtures`, `upcoming`, `results`, `groups`.
        """

        return self._http_get(endpoint='seasons', includes=includes)

    def season_results(self, season_id: int, includes: tuple = tuple()) -> List[Dict]:
        """ Returns completed fixtures of a season.

        Parameter ``includes`` specifies objects to include in the response. Maximum level of includes allowed is 1.
        Valid objects are: `localTeam`, `visitorTeam`, `substitutions`, `goals`, `cards`, `other`, `corners`,
        `lineup`, `bench`, `sidelined`, `stats`, `comments`, `tvstations`, `highlights`, `league`, `season`, `round`,
        `stage`, `referee`, `events`, `venue`, `odds`, `flatOdds`, `inplay`, `localCoach`, `visitorCoach`, `group`,
        `trends`.
        """

        includes = ('results',) + tuple(['results.' + inc for inc in includes])
        return self.season(season_id=season_id, includes=includes)['results']

    def fixtures(self, start_date: date, end_date: date, league_ids: List[int] = None,
                 includes: tuple = None) -> List[Dict]:
        """ Returns fixtures between ``start_date`` and ``end_date``. The dates are inclusive.

        Parameter ``league_ids`` specifies leagues from which the fixtures will be returned, defaulting to all leagues.

        Parameter ``includes`` specifies objects to include in the response. Maximum level of includes allowed is 3.
        Valid objects are: `localTeam`, `visitorTeam`, `substitutions`, `goals`, `cards`, `other`, `corners`,
        `lineup`, `bench`, `sidelined`, `stats`, `comments`, `tvstations`, `highlights`, `league`, `season`, `round`,
        `stage`, `referee`, `events`, `venue`, `odds`, `flatOdds`, `inplay`, `localCoach`, `visitorCoach`, `group`,
        `trends`.
        """

        endpoint = join('fixtures', 'between', start_date.strftime('%Y-%m-%d'), end_date.strftime('%Y-%m-%d'))
        return self._http_get(endpoint=endpoint, params={'leagues': league_ids or []}, includes=includes)

    def fixture(self, fixture_id: int, includes: tuple = None) -> Dict:
        """ Returns a fixture.

        Parameter ``includes`` specifies objects to include in the response. Maximum level of includes allowed is 10.
        Valid objects are: `localTeam`, `visitorTeam`, `substitutions`, `goals`, `cards`, `other`, `corners`,
        `lineup`, `bench`, `sidelined`, `stats`, `comments`, `tvstations`, `highlights`, `league`, `season`, `round`,
        `stage`, `referee`, `events`, `venue`, `odds`, `flatOdds`, `inplay`, `localCoach`, `visitorCoach`, `group`,
        `trends`.
        """

        return self._http_get(endpoint=join('fixtures', str(fixture_id)), includes=includes)

    def team_fixtures(self, start_date: date, end_date: date, team_id: int, includes: tuple = None) -> List[Dict]:
        """ Returns fixtures between ``start_date`` and ``end_date`` for a team specified by ``team_id``.

        Parameter ``includes`` specifies objects to include in the response. Maximum level of includes allowed is 3.
        Valid objects are: `localTeam`, `visitorTeam`, `substitutions`, `goals`, `cards`, `other`, `corners`,
        `lineup`, `bench`, `sidelined`, `stats`, `comments`, `tvstations`, `highlights`, `league`, `season`, `round`,
        `stage`, `referee`, `events`, `venue`, `odds`, `flatOdds`, `inplay`, `localCoach`, `visitorCoach`, `group`,
        `trends`.
        """

        endpoint = join('fixtures', 'between', start_date.strftime('%Y-%m-%d'), end_date.strftime('%Y-%m-%d'),
                        str(team_id))
        return self._http_get(endpoint=endpoint, includes=includes)

    def fixtures_today(self, league_ids: List[int] = None, includes: tuple = None) -> List[Dict]:
        """ Returns today's fixtures, played and to be played.

        Parameter ``league_ids`` specifies leagues from which the fixtures will be returned, defaulting to all leagues.

        Parameter ``includes`` specifies objects to include in the response. Maximum level of includes allowed is 10.
        Valid objects are: `localTeam`, `visitorTeam`, `substitutions`, `goals`, `cards`, `other`, `corners`,
        `lineup`, `bench`, `sidelined`, `stats`, `comments`, `tvstations`, `highlights`, `league`, `season`, `round`,
        `stage`, `referee`, `events`, `venue`, `odds`, `flatOdds`, `inplay`, `localCoach`, `visitorCoach`, `group`,
        `trends`.
        """

        return self._http_get(endpoint='livescores', params={'leagues': league_ids or []}, includes=includes)

    def fixtures_in_play(self, includes: tuple = None) -> List[Dict]:
        """ Returns in-play fixtures. Note that in-play is defined by SportMonks as fixtures currently played,
        plus fixtures that will begin within 45 minutes, and fixtures that ended less than 30 minutes ago.

        Parameter ``includes`` specifies objects to include in the response. Maximum level of includes allowed is 10.
        Valid objects are: `localTeam`, `visitorTeam`, `substitutions`, `goals`, `cards`, `other`, `corners`,
        `lineup`, `bench`, `sidelined`, `stats`, `comments`, `tvstations`, `highlights`, `league`, `season`, `round`,
        `stage`, `referee`, `events`, `venue`, `odds`, `flatOdds`, `inplay`, `localCoach`, `visitorCoach`, `group`,
        `trends`.
        """

        return self._http_get(endpoint=join('livescores', 'now'), includes=includes)

    def head_to_head_fixtures(self, team_ids: set, includes: tuple = None) -> List[Dict]:
        """ Returns all head-to-head fixtures of two teams specified by ``team_ids``.

        Parameter ``includes`` specifies objects to include in the response. Maximum level of includes allowed is 2.
        Valid objects are:	`localTeam`, `visitorTeam`, `substitutions`, `goals`, `cards`, `other`, `lineup`, `bench`,
        `stats`, `comments`, `tvstations`, `highlights`, `league`, `season`, `round`, `stage`, `referee`, `events`,
        `venue`, `trends`.
        """

        team_ids = list(team_ids)
        endpoint = join('head2head', str(team_ids[0]), str(team_ids[1]))
        return self._http_get(endpoint=endpoint, includes=includes)

    def commentaries(self, fixture_id: int) -> List:
        """ Returns commentaries of a fixture. Not all fixtures have commentaries. If a fixture has no commentaries then
        an empty list is returned.
        """

        return self._http_get(endpoint=join('commentaries', 'fixture', str(fixture_id)))

    def video_highlights(self, fixture_id: int = None, includes: tuple = None) -> List[Dict]:
        """ Returns links to video highlights of all fixtures or of a fixture specified by ``fixture_id``.

        Parameter ``includes`` specifies objects to include in the response. Maximum level of includes allowed is 2.
        Valid objects are:	`fixture`.
        """

        endpoint = 'highlights'

        if fixture_id:
            endpoint = join('highlights', 'fixture', str(fixture_id))

        return self._http_get(endpoint=endpoint, includes=includes)

    def standings(self, season_id: int, live: bool = False, group_id: int=None, includes: tuple = None) -> List[Dict]:
        """ Returns standings of a season.

        Parameter ``live`` specifies whether standings should also take into account in-play fixtures.

        Parameter ``group_id`` specifies for which group to return the standings. Groups are found in tournaments like
        the FIFA World Cup (e.g. Group A has group ID 185).

        Parameter ``includes`` specifies objects to include in the response. Maximum level of includes allowed is 2.
        Valid objects are: `team`, `league`, `season`, `round`, `stage`.
        """

        endpoint = join('standings', 'season', str(season_id))

        if live:
            endpoint = join('standings', 'season', 'live', str(season_id))

        return self._http_get(endpoint=endpoint, includes=includes, params={'group_id': group_id})

    def teams(self, season_id: int, includes: tuple = None) -> List[Dict]:
        """ Returns all teams that played during a season.

        Parameter ``includes`` specifies objects to include in the response. Maximum level of includes allowed is 3.
        Valid objects are: `country`, `squad`, `coach`, `transfers`, `sidelined`, `stats`, `venue`, `fifaranking`,
        `uefaranking`, `visitorFixtures`, `localFixtures`, `visitorResults`, `localResults`, `latest`, `upcoming`.
        """

        return self._http_get(endpoint=join('teams', 'season', str(season_id)), includes=includes)

    def team(self, team_id: int, includes: tuple=None) -> Dict:
        """ Returns a team.

        Parameter ``includes`` specifies objects to include in the response. Maximum level of includes allowed is 3.
        Valid objects are: `country`, `squad`, `coach`, `transfers`, `sidelined`, `stats`, `venue`, `fifaranking`,
        `uefaranking`, `visitorFixtures`, `localFixtures`, `visitorResults`, `localResults`, `latest`, `upcoming`.
        """

        return self._http_get(endpoint=join('teams', str(team_id)), includes=includes)

    def team_stats(self, team_id: int) -> Dict:
        """ Returns stats of a team. """

        return self._http_get(endpoint=join('teams', str(team_id)), includes=('stats',))['stats']

    def top_scorers(self, season_id: int, includes: tuple=None) -> Dict:
        """ Returns top scorers of a season. Three types of top scorers are returned: most goals, most assists, and most
        cards.

        Parameter ``includes`` specifies objects to include in the response. Maximum level of includes allowed is 3.
        Valid objects are: `goalscorers.player`, `goalscorers.team` `cardscorers.player`, `cardscorers.team`,
        `assistscorers.player`, `assistscorers.team`.
        """

        endpoint = join('topscorers', 'season', str(season_id))
        return self._http_get(endpoint=endpoint, includes=includes)

    def venue(self, venue_id: int) -> Dict:
        """ Returns a venue. """

        return self._http_get(endpoint=join('venues', str(venue_id)))

    def rounds(self, season_id: int, includes: tuple=None) -> List[Dict]:
        """ Returns rounds of a season.

        Parameter ``includes`` specifies objects to include in the response. Maximum level of includes allowed is 2.
        Valid objects are: `fixtures`, `results`, `season`, `league`.
        """

        return self._http_get(endpoint=join('rounds', 'season', str(season_id)), includes=includes)

    def round(self, round_id: int, includes: tuple=None) -> Dict:
        """ Returns a round.

        Parameter ``includes`` specifies objects to include in the response. Maximum level of includes allowed is 2.
        Valid objects are: `fixtures`, `results`, `season`, `league`.
        """

        return self._http_get(endpoint=join('rounds', str(round_id)), includes=includes)

    def pre_match_odds(self, fixture_id: int) -> List[Dict]:
        """ Returns pre-match odds of a fixture. """

        return self._http_get(endpoint=join('odds', 'fixture', str(fixture_id)))

    def in_play_odds(self, fixture_id: int) -> List[Dict]:
        """ Returns in-play odds of a fixture. """

        return self._http_get(endpoint=join('odds', 'inplay', 'fixture', str(fixture_id)))

    def player(self, player_id: int) -> Dict:
        """ Returns a player. """

        return self._http_get(endpoint=join('players', str(player_id)))

    def squad(self, season_id: int, team_id: int, includes: tuple=None) -> List[Dict]:
        """ Returns a squad. A squad is a set of players that played for a team during a season.

        Parameter ``includes`` specifies objects to include in the response. Maximum level of includes allowed is 3.
        Valid objects are: `player`, `position`.
        """

        return self._http_get(endpoint=join('squad', 'season', str(season_id), 'team', str(team_id)), includes=includes)

    def stage(self, stage_id: int, includes: tuple=None) -> Dict:
        """ Returns a stage.

        Parameter ``includes`` specifies objects to include in the response. Maximum level of includes allowed is 2.
        Valid objects are: `fixtures`, `results`, `season`, `league`.
        """

        return self._http_get(endpoint=join('stages', str(stage_id)), includes=includes)

    def season_stages(self, season_id: int, includes: tuple=None) -> List[Dict]:
        """ Returns stages of a season.

        Parameter ``includes`` specifies objects to include in the response. Maximum level of includes allowed is 2.
        Valid objects are: `fixtures`, `results`, `season`, `league`.
        """

        return self._http_get(endpoint=join('stages', 'season', str(season_id)), includes=includes)

    def fixture_tv_stations(self, fixture_id: int) -> List[Dict]:
        """ Returns tv stations broadcasting specified fixture. """

        return self._http_get(endpoint=join('tvstations', 'fixture', str(fixture_id)))

    def season_venues(self, season_id: int) -> List[Dict]:
        """ Returns venues of specified season. """

        return self._http_get(endpoint=join('venues', 'season', str(season_id)))

    def markets(self) -> List[Dict]:
        """ Returns all betting markets, e.g. '3Way Result', 'Home/Away'. """

        return self._http_get(endpoint='markets')

    def market(self, market_id: int) -> Dict:
        """ Returns a market. """

        return self._http_get(endpoint=join('markets', str(market_id)))

    def coach(self, coach_id: int) -> Dict:
        """ Returns a coach. """

        return self._http_get(endpoint=join('coaches', str(coach_id)))
